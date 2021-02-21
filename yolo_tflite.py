from postprocess_np import yolo3_postprocess_np #YOLOv3出力の整形
import cv2
#import tensorflow as tf
from tflite_runtime.interpreter import Interpreter
import numpy as np
import time
import tkinter as tk
from PIL import Image,ImageTk
import sqlite3
import threading

from serial_device import ir_serial #irMagicianとの通信用

from pysinewave import SineWave
import sounddevice as sd
import sys

sinewave = SineWave(pitch = 5, pitch_per_second = 30,decibels_per_second = 1)
sinewave.set_volume(0)

def callback(sinewave,outdata,frames,time,status):
    if status:
        print(status,file=sys.stderr)
    try:
        data = sinewave.sinewave_generator.next_data(frames)
        outdata[:] = data.reshape(-1,1)
    except Exception as e:
        print(e)

sinewave.output_stream = sd.OutputStream(channels=1,callback= lambda *args: callback(sinewave,*args),samplerate=44100)
#sinewave.sinewave_generator.set_amplitude(0.1)

def sineplay(sinewave,freq):
    try:
        #cur_time = time.time()
        #print((cur_time - before_time) > 1)
        #sinewave.set_volume(0)
        sinewave.set_frequency(freq)
        # Turn the sine wave on.
        sinewave.play()
    except Exception as e:
        print(e)


def sinestop(sinewave):
    #sinewave.set_frequency(0)
    #sinewave.set_volume(-1000)
    #time.sleep(0.05)
    sinewave.stop()


#IoU計算関数
def intersection_over_union(box_1, box_2):
    width_of_overlap_area = min(box_1[2], box_2[2]) - max(box_1[0], box_2[0])
    height_of_overlap_area = min(box_1[3], box_2[3]) - max(box_1[1], box_2[1])
    if width_of_overlap_area < 0 or height_of_overlap_area < 0:
        area_of_overlap = 0
    else:
        area_of_overlap = width_of_overlap_area * height_of_overlap_area
    box_1_area = (box_1[3] - box_1[1]) * (box_1[2] - box_1[0])
    box_2_area = (box_2[3] - box_2[1]) * (box_2[2] - box_2[0])
    area_of_union = box_1_area + box_2_area - area_of_overlap
    if area_of_union == 0:
        return 0
    return area_of_overlap / area_of_union

#class_idをラベルに変換する辞書
idx2label = {0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"three_v2",7:"fit",8:"fox",9:"ok",10:"go",11:"little_finger"}
#anchors = [151,288, 171,191, 209,296, 105,90, 120,136, 126,181, 68,101, 86,129, 98,162]
#anchors = [72,79, 93,159, 96,106, 56,68, 56,47, 70,105, 37,55, 45,75, 56,90]
anchors = [81,155, 95,106, 112,162, 57,85, 64,61, 71,94, 36,58, 47,72, 49,40]
#anchors = [155,284, 209,275, 114,114, 130,176, 75,105, 94,148]
#anchors = [189,170, 209,240, 248,311, 124,184, 155,236, 178,306]
anchors = np.array(anchors).reshape(-1, 2)

def resize_image(img, size=(28,28)):

    h, w = img.shape[:2]
    c = img.shape[2] if len(img.shape)>2 else 1

    if h == w: 
        return cv2.resize(img, size, cv2.INTER_AREA)

    dif = h if h > w else w

    interpolation = cv2.INTER_AREA if dif > (size[0]+size[1])//2 else cv2.INTER_CUBIC

    x_pos = (dif - w)//2
    y_pos = (dif - h)//2

    if len(img.shape) == 2:
        mask = np.zeros((dif, dif), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w] = img[:h, :w]
    else:
        mask = np.zeros((dif, dif, c), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w, :] = img[:h, :w, :]

    return cv2.resize(mask, size, interpolation)


#YOLOv3でジェスチャを認識するクラス
class YOLO:
    def __init__(self):
        #self.interpreter = tf.lite.Interpreter("./weights/mnsy_fp16_quant.tflite",num_threads=2)
        #self.interpreter = Interpreter("./weights/tiny-yolov4_quant224.tflite",num_threads=4)
        self.interpreter = Interpreter("./weights/mnsy224_quant.tflite",num_threads=4)
        
        self.cnt = 0 #stopジェスチャのカウント

        self.stop = False #動作停止flag
        self.checker = None #画面更新flag
        
        self.before_data = None #1つ前のデータを保持
        self.start_point_x = None #ジェスチャの開始座標
        self.start_point_y = None #ジェスチャの開始座標
        self.detected_data = [] #過去のデータを保持するリスト
        self.detect_class = np.empty(0) #median値を計算するための配列
        self.exec_f = None #実行フレームへのアクセス変数

        self.count = 0 #ジェスチャ時間閾値
        self.y_start2end_count = None #ジェスチャ開始からのフレーム待機時間
        self.x_start2end_count = None #ジェスチャ開始からのフレーム待機時間

        self.end_point_x = None #ジェスチャの終了座標
        self.end_point_y = None #ジェスチャの終了座標
        
        self.preview = None
        self.preview_frame = None
        self.image_texture = None
        self.detect_gesture_name = ""
        self.frame_counter = 0
        self.diff_threshold = 50#ジェスチャ移動距離閾値
        self.furniture = "tv"
        self.use_camera = None
        self.use_sound = None

    def set_exec_f(self,exec_f):
        self.exec_f = exec_f #ExecuteFrame
        
    def set_furniture(self,furniture):
        self.furniture = furniture
    
    def setCameraPreview(self,preview):
        self.preview = preview


    #モデルを実行してジェスチャ検出(tkinter用)
    def exec_model(self):
        self.interpreter.allocate_tensors()
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        print(input_details)
        inputs = self.interpreter.tensor(input_details[0]['index'])
        output1 = self.interpreter.tensor(output_details[0]['index'])
        output2 = self.interpreter.tensor(output_details[1]['index'])
        output3 = self.interpreter.tensor(output_details[2]['index'])

        #time_stamp = time.time()
        cap = cv2.VideoCapture(0)
        time_stamp = 0
        start_flag_x = 0
        start_flag_y = 0
        #end_flag_y = 0
        speed_count = 0#仮
        speed_sum = 0#仮
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap_w = cap.get(3)
        cap_h = cap.get(4)
        #cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        while cap.isOpened():
            #time.sleep(0.1)
            t = 0
            start_time = time.time()
            #time.sleep(0.03)
            ret, frame = cap.read()
            #左右反転(鏡)
            frame = cv2.flip(frame,1)
            if not ret:
                break

            #STEP-6
            model_n,model_w,model_h,model_c = input_details[0]['shape']
            in_frame = cv2.resize(frame, (model_w, model_h))
            #in_frame = resize_image(frame,size=(224,224))
            #frame  =  resize_image(frame,size=(600,600))
            in_frame = cv2.cvtColor(in_frame,cv2.COLOR_BGR2RGB)
            in_frame = cv2.normalize(in_frame,None,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_32F)
            in_frame = in_frame.reshape((model_n, model_h, model_w, model_c))

            #STEP-7
            inputs().setfield(in_frame,dtype=np.float32)
            self.interpreter.invoke()
            current_time = time.time()
            #tは実行にかかった時間(速度計算に使用)
            t = current_time - start_time

            #疑似的にラズパイ実行時の速度にする
            """try:
                time.sleep(0.08-t)
            except:
                pass
            t = current_time - start_time + (0.08-t)"""
            
            objects = yolo3_postprocess_np([output1(),output2(),output3()],frame.shape[:-1],anchors,12,(model_h,model_w),confidence=0.35)
            speed_count += 1
            speed_sum += t
            iou_threshold = 0.1
            for i in range(len(objects[0])):
                if objects[3][i] == 0:
                    continue
                for j in range(i + 1, len(objects[0])):
                    if intersection_over_union(objects[1][i], objects[1][j]) > iou_threshold:
                        objects[3][j] = 0
            velocity_x = 0
            velocity_y = 0
            sineplay_count = 0
            #time_stamp = time.time()
            
            #for i in range(len(objects[0])):
            if len(objects[0]) > 0:
                i = 0
                #(メモ)confidence=0.45,classprob=0.3
                if objects[3][i] > 0.1:
                    #print(objects)
                    x_center = objects[0][i][0]
                    y_center = objects[0][i][1]
                    class_id = objects[2][i]
                    if self.detect_class.__len__() == 9:
                        #class_idのmedianを計算して検出クラスを安定させる
                        median_class_id = np.median(self.detect_class)
                        frame = cv2.rectangle(frame,(objects[1][i][0],objects[1][i][1]),(objects[1][i][2],objects[1][i][3]),(0,255,0),3)
                        frame = cv2.putText(frame,idx2label[median_class_id],(objects[1][i][0]-3,objects[1][i][1]-3), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255),3)
                        frame = cv2.line(frame,(x_center,y_center),(x_center+1,y_center+1),(0,255,0),3)
                        time_stamp = time.time()
                        
                        if self.before_data != None and t != 0:
                            #速度を計算
                            velocity_x = (self.before_data[0]-x_center)/t
                            velocity_y = (self.before_data[1]-y_center)/t
                            #print(velocity_y)
                        
                        if self.detect_gesture_name == "":
                            if self.start_point_x == None and self.cnt > 5 and self.end_point_y == None:
                                start_flag_x = 1
                                if self.use_sound == 1:
                                    sineplay(sinewave,400)
                                    sineplay_count += 1
                            
                            if self.start_point_y == None and self.cnt > 5 and self.end_point_x == None:
                                start_flag_y = 1
                                if self.use_sound == 1:
                                    sineplay(sinewave,400)
                                    sineplay_count += 1
                            
                            if start_flag_x >= 1:
                                start_flag_x += 1
                            
                            #カウント6以上でリセット
                            if start_flag_x > 5:
                                start_flag_x = 0
                                self.start_point_x = None
                                #print("reset x")
                            
                            if start_flag_y >= 1:
                                start_flag_y += 1
                            
                            #カウント6以上でリセット
                            if start_flag_y > 5:
                                start_flag_y = 0
                                self.start_point_y = None
                                #print("reset y")
                            
                            if start_flag_x >= 1 and abs(velocity_x) > 400:
                                self.start_point_x = (x_center,velocity_x,median_class_id)
                                self.x_start2end_count = 0
                                start_flag_x = 0
                                self.cnt = 0
                                if self.use_sound == 1:
                                    freq = (x_center/cap_w)*500+100
                                    sineplay(sinewave,freq)
                                    sineplay_count += 1
                            #ジェスチャ開始後、数フレームの間待機する
                            if self.x_start2end_count != None:
                                self.x_start2end_count += 1
                                if self.use_sound == 1:
                                    freq = (x_center/cap_w)*500+100
                                    sineplay(sinewave,freq)
                                    sineplay_count += 1
                            
                            if self.start_point_x != None and self.end_point_x == None and self.x_start2end_count > 5 and self.cnt > 3:#abs(velocity_x) < 90:
                                self.end_point_x = (x_center,median_class_id)
                                self.x_start2end_count = None #初期化
                                if self.use_sound == 1:
                                    freq = (x_center/cap_w)*500+100
                                    sineplay(sinewave,freq)
                                    sineplay_count += 1
                            
                            if self.end_point_x != None and self.cnt > 3:#3
                                diff = self.start_point_x[0] - self.end_point_x[0]
                                if self.start_point_x[2] == median_class_id:
                                    if diff > 0:
                                        if self.start_point_x[1] > 0 and abs(diff) > self.diff_threshold:
                                            print(idx2label[median_class_id],"left")
                                            self.detect_gesture_name = idx2label[median_class_id] + " left"
                                            self.frame_counter = 0
                                            sinestop(sinewave)
                                            threading.Thread(target=self.Infrared_signal_control,args=(median_class_id,4)).start()
                                    else:
                                        if self.start_point_x[1] < 0 and abs(diff) > self.diff_threshold:
                                            print(idx2label[median_class_id],"right")
                                            self.detect_gesture_name = idx2label[median_class_id] + " right"
                                            self.frame_counter = 0
                                            sinestop(sinewave)
                                            threading.Thread(target=self.Infrared_signal_control,args=(median_class_id,3)).start()
                            
                                start_flag_x = 0
                                self.start_point_x = None
                                self.end_point_x = None
                            
                            #y
                            #if start_flag_y >= 1 and abs(velocity_y) > 300 and self.y_start2end_count == None:
                            if start_flag_y >= 1 and abs(velocity_y) > 400:
                                self.start_point_y = (y_center,velocity_y,median_class_id)
                                self.y_start2end_count = 0
                                start_flag_y = 0
                                print(self.start_point_y)
                                if self.use_sound == 1:
                                    freq = ((cap_h-y_center)/cap_h)*500+100
                                    sineplay(sinewave,freq)
                                    sineplay_count += 1
                            #ジェスチャ開始後、数フレームの間待機する
                            if self.y_start2end_count != None:
                                self.y_start2end_count += 1
                                if self.use_sound == 1:
                                    freq = ((cap_h-y_center)/cap_h)*500+100
                                    sineplay(sinewave,freq)
                                    sineplay_count += 1
                            
                            #if self.start_point_y != None and self.end_point_y == None and abs(velocity_y) < 90:
                            if self.start_point_y != None and self.end_point_y == None and self.y_start2end_count > 5 and self.cnt > 3:#abs(velocity_y) < 90:
                                self.end_point_y = (y_center,median_class_id)
                                self.y_start2end_count = None #初期化
                                if self.use_sound == 1:
                                    freq = ((cap_h-y_center)/cap_h)*500+100
                                    sineplay(sinewave,freq)
                                    sineplay_count += 1
                                print(self.end_point_y)
                            
                            if self.end_point_y != None and self.cnt > 3:#3
                                diff = self.start_point_y[0] - self.end_point_y[0]
                                if self.start_point_y[2] == median_class_id:
                                    if diff > 0:
                                        if self.start_point_y[1] > 0 and abs(diff) > self.diff_threshold:
                                            print(idx2label[median_class_id],"up")
                                            self.detect_gesture_name = idx2label[median_class_id] + " up"
                                            self.frame_counter = 0
                                            sinestop(sinewave)
                                            threading.Thread(target=self.Infrared_signal_control,args=(median_class_id,1)).start()
                                    else:
                                        if self.start_point_y[1] < 0 and abs(diff) > self.diff_threshold:
                                            print(idx2label[median_class_id],"down")
                                            self.detect_gesture_name = idx2label[median_class_id] + " down"
                                            self.frame_counter = 0
                                            sinestop(sinewave)
                                            threading.Thread(target=self.Infrared_signal_control,args=(median_class_id,2)).start()
                            
                                start_flag_y = 0
                                end_flag_y = 0
                                self.start_point_y = None
                                self.end_point_y = None


                            if self.before_data != None:
                                if abs(self.before_data[0] - x_center) < 30 and abs(self.before_data[1] - y_center) < 30 and self.before_data[2] == median_class_id:
                                    self.cnt += 1
                                else:
                                    self.cnt = 0
                                    
                            #if self.cnt > (1/t)*2.5:
                            if self.cnt > 20:
                                print(idx2label[median_class_id],"stop")
                                self.detect_gesture_name = idx2label[median_class_id] + " stop"
                                self.frame_counter = 0
                                sinestop(sinewave)
                                threading.Thread(target=self.Infrared_signal_control,args=(median_class_id,0)).start()
                                self.cnt = 0
                        
                        #現在のデータを過去のデータとして保持
                        self.before_data = (x_center,y_center,median_class_id)
                    #median_filterで計算するための配列を更新
                    if self.detect_class.__len__() < 9:
                        self.detected_data = [[x_center,y_center,0,0,class_id] for _ in range(9)]
                        #最初のみすべてのデータを現在のclass_idでfillする
                        self.detect_class = np.array([class_id for _ in range(9)])
                    else:
                        self.detected_data.pop(0)
                        self.detected_data.append([x_center,y_center,velocity_x,velocity_y,median_class_id])
                        self.detect_class = np.append(self.detect_class[1:],class_id)
                    
                    #print(np.average(self.detected_data,axis=0)[3])


                    #print("速度x:",velocity_x)
                    #print("カウント:",self.cnt)
                    #print("フラッグx:",start_flag_x)
                    #print("フラッグy:",start_flag_y)
            print(time.time() - time_stamp)
            if time.time() - time_stamp > 1:
                #print("reset")
                #time_stamp = time.time()
                sinestop(sinewave)
                self.start_point_x = None
                self.start_point_y = None
                self.x_start2end_count = None
                self.y_start2end_count = None
                self.before_data = None
                self.end_point_x = None
                self.end_point_y = None
                self.cnt = 0
            
            self.frame_counter += 1
            if self.frame_counter > (1/t)*2:
                self.detect_gesture_name = ""
                self.frame_counter = 0

            #frame = cv2.putText(frame,str(round(1/t,1))+"fps",(30,40),cv2.FONT_HERSHEY_PLAIN,3,(0,0,255),3)
            frame = cv2.putText(frame,self.detect_gesture_name,(0,int(cap_h//10)),cv2.FONT_HERSHEY_PLAIN,cap_h//130,(0,0,255),3)            

            print("呼び出し回数:",sineplay_count)
            #表示サイズにリサイズ
            frame = cv2.resize(frame,(600,400))
            self.preview_frame = frame
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            print(self.use_camera == 1)
            if self.use_camera == 1:
                #以前の描画更新結果と異なる場合は映像を描画
                if self.checker != img:
                    self.exec_f.canvas.create_image((0,0),image=img,anchor=tk.NW,tag="img")
                    self.checker = img
            #停止信号が渡された場合にキャンバスを初期化しloopを抜ける
            if self.stop:
                self.exec_f.canvas.delete("all")
                sinestop(sinewave)
                print("実行速度:",speed_sum/speed_count*1000,"ms")
                break
        cap.release()

    
    def exec_model_v2(self):
        self.interpreter.allocate_tensors()
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        print(input_details)
        inputs = self.interpreter.tensor(input_details[0]['index'])
        output1 = self.interpreter.tensor(output_details[0]['index'])
        output2 = self.interpreter.tensor(output_details[1]['index'])
        output3 = self.interpreter.tensor(output_details[2]['index'])

        #time_stamp = time.time()
        cap = cv2.VideoCapture(0)
        time_stamp = 0
        start_flag_x = 0
        start_flag_y = 0
        #end_flag_y = 0
        speed_count = 0#仮
        speed_sum = 0#仮
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap_w = cap.get(3)
        cap_h = cap.get(4)
        #cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        while cap.isOpened():
            #time.sleep(0.1)
            t = 0
            start_time = time.time()
            #time.sleep(0.03)
            ret, frame = cap.read()
            #左右反転(鏡)
            frame = cv2.flip(frame,1)
            if not ret:
                break

            #STEP-6
            model_n,model_w,model_h,model_c = input_details[0]['shape']
            in_frame = cv2.resize(frame, (model_w, model_h))
            #in_frame = resize_image(frame,size=(224,224))
            #frame  =  resize_image(frame,size=(600,600))
            in_frame = cv2.cvtColor(in_frame,cv2.COLOR_BGR2RGB)
            in_frame = cv2.normalize(in_frame,None,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_32F)
            in_frame = in_frame.reshape((model_n, model_h, model_w, model_c))

            #STEP-7
            inputs().setfield(in_frame,dtype=np.float32)
            self.interpreter.invoke()
            current_time = time.time()
            #tは実行にかかった時間(速度計算に使用)
            t = current_time - start_time

            #疑似的にラズパイ実行時の速度にする
            """try:
                time.sleep(0.08-t)
            except:
                pass
            t = current_time - start_time + (0.08-t)"""
            
            objects = yolo3_postprocess_np([output1(),output2(),output3()],frame.shape[:-1],anchors,12,(model_h,model_w),confidence=0.45)
            speed_count += 1
            speed_sum += t
            iou_threshold = 0.1
            for i in range(len(objects[0])):
                if objects[3][i] == 0:
                    continue
                for j in range(i + 1, len(objects[0])):
                    if intersection_over_union(objects[1][i], objects[1][j]) > iou_threshold:
                        objects[3][j] = 0
            velocity_x = 0
            velocity_y = 0
            sineplay_count = 0
            #time_stamp = time.time()
            
            #for i in range(len(objects[0])):
            if len(objects[0]) > 0:
                i = 0
                #(メモ)confidence=0.45,classprob=0.3
                if objects[3][i] > 0.1:
                    #print(objects)
                    x_center = objects[0][i][0]
                    y_center = objects[0][i][1]
                    class_id = objects[2][i]
                    if self.detect_class.__len__() == 9:
                        #class_idのmedianを計算して検出クラスを安定させる
                        median_class_id = np.median(self.detect_class)
                        frame = cv2.rectangle(frame,(objects[1][i][0],objects[1][i][1]),(objects[1][i][2],objects[1][i][3]),(0,255,0),3)
                        frame = cv2.putText(frame,idx2label[median_class_id],(objects[1][i][0]-3,objects[1][i][1]-3), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255),3)
                        frame = cv2.line(frame,(x_center,y_center),(x_center+1,y_center+1),(0,255,0),3)
                        time_stamp = time.time()
                        
                        if self.before_data != None and t != 0:
                            #速度を計算
                            velocity_x = (self.before_data[0]-x_center)/t
                            velocity_y = (self.before_data[1]-y_center)/t
                            #print(velocity_y)
                        
                        if self.detect_gesture_name == "":
                            pass
                        #現在のデータを過去のデータとして保持
                        self.before_data = (x_center,y_center,median_class_id)
                    #median_filterで計算するための配列を更新
                    if self.detect_class.__len__() < 9:
                        self.detected_data = [[x_center,y_center,0,0,class_id] for _ in range(9)]
                        #最初のみすべてのデータを現在のclass_idでfillする
                        self.detect_class = np.array([class_id for _ in range(9)])
                    else:
                        self.detected_data.pop(0)
                        self.detected_data.append([x_center,y_center,velocity_x,velocity_y,median_class_id])
                        self.detect_class = np.append(self.detect_class[1:],class_id)
                    
                    #print(np.average(self.detected_data,axis=0)[3])

            print(time.time() - time_stamp)
            if time.time() - time_stamp > 1:
                #print("reset")
                #time_stamp = time.time()
                sinestop(sinewave)
                self.start_point_x = None
                self.start_point_y = None
                self.x_start2end_count = None
                self.y_start2end_count = None
                self.before_data = None
                self.end_point_x = None
                self.end_point_y = None
                self.cnt = 0
            
            self.frame_counter += 1
            if self.frame_counter > (1/t)*2:
                self.detect_gesture_name = ""
                self.frame_counter = 0

            #frame = cv2.putText(frame,str(round(1/t,1))+"fps",(30,40),cv2.FONT_HERSHEY_PLAIN,3,(0,0,255),3)
            frame = cv2.putText(frame,self.detect_gesture_name,(0,int(cap_h//10)),cv2.FONT_HERSHEY_PLAIN,cap_h//130,(0,0,255),3)            

            print("呼び出し回数:",sineplay_count)
            #表示サイズにリサイズ
            frame = cv2.resize(frame,(600,400))
            self.preview_frame = frame
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            print(self.use_camera == 1)
            if self.use_camera == 1:
                #以前の描画更新結果と異なる場合は映像を描画
                if self.checker != img:
                    self.exec_f.canvas.create_image((0,0),image=img,anchor=tk.NW,tag="img")
                    self.checker = img
            #停止信号が渡された場合にキャンバスを初期化しloopを抜ける
            if self.stop:
                self.exec_f.canvas.delete("all")
                sinestop(sinewave)
                print("実行速度:",speed_sum/speed_count*1000,"ms")
                break
        cap.release()


    #ジェスチャに対応した赤外線信号を発信する
    def Infrared_signal_control(self,class_id,move_id):
        target_id = 5*class_id + move_id
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        print("target_id",target_id)
        cursor.execute("SELECT * FROM {} WHERE target_id = {}".format(self.furniture,str(target_id)))
        res = cursor.fetchall()
        print(res)
        if len(res) != 0:
            self.playIR(res[0])
    
    #引数で与えられた赤外線信号を発信する
    def playIR(self,data):
        print("Playing IR")
        rawdata = data[4].split(",")
        rawdata = [int(d) for d in rawdata]
        recNumber = len(rawdata)
        rawX = rawdata

        ir_serial.write(("n,%d\r\n" % recNumber).encode())
        ir_serial.readline()

        postScale = data[2]
        ir_serial.write(("k,%d\r\n" % postScale).encode())
        #time.sleep(1.0)
        msg = ir_serial.readline()
    
        for n in range(recNumber):
            bank = n / 64
            pos = n % 64
            if (pos == 0):
                ir_serial.write(("b,%d\r\n" % bank).encode())
    
            ir_serial.write(("w,%d,%d\n\r" % (pos, rawX[n])).encode())
    
        ir_serial.write("p\r\n".encode())
        msg = ir_serial.readline()
        print(msg)

#オブジェクトを生成
yolo_obj = YOLO()