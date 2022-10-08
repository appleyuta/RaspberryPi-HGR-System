import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import threading
import sqlite3

from PIL import Image,ImageTk

import sys
import serial
import time
import json
import argparse
import os
from serial_device import ir_serial
import re

#furniture_idを追加することで家電ごとに赤外線信号を登録できるようにする
#CREATE TABLE IF NOT EXISTS sample (id INTEGER PRIMARY KEY, furniture_id INTEGER,irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)

class CountWindow(tk.Toplevel):
    def __init__(self,master=None,**kwargs):
        tk.Toplevel.__init__(self,master,**kwargs)
        self.count = 0
        self.label = tk.Label(self, text = "irMagicianに向けてリモコンのボタンを押して赤外線登録")
        self.label2 = tk.Label(self, text = str(self.count)+"秒")
        self.label.pack()
        self.label2.pack()
        self.focus()
        self.attributes("-topmost", True) #最前面表示
        self.grab_set()
        self.id = None
        self.protocol('WM_DELETE_WINDOW', (lambda: 'pass')())

    
    def timer(self):
        self.count += 1
        self.label2.configure(text=str(self.count)+"秒")
        if self.count <= 2:
            self.id = self.after(1000,self.timer)
        else:
            self.after_cancel(self.id)
    
    def register_waiting(self):
        self.label2.configure(text="赤外線をデータベースに登録中です")



class InfraredSignalRegisterFrame(tk.Frame):
    def __init__(self,setting_f,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=700)
        self.label = tk.Label(self,text="赤外線登録",font=font.Font(size=30))
        self.furniture_idx2label = {0:"tv",1:"aircon",2:"radio",3:"light",4:"other"}
        self.furniture_name = tk.StringVar(value="tv")
        self.tv_img = Image.open("./furniture_image/tv.png").resize((50,50))
        self.tv_img = ImageTk.PhotoImage(self.tv_img)
        self.select_tv = ttk.Button(self,text="テレビ",image=self.tv_img,compound="top")
        self.aircon_img = Image.open("./furniture_image/aircon.png").resize((50,50))
        self.aircon_img = ImageTk.PhotoImage(self.aircon_img)
        self.select_aircon = ttk.Button(self,text="エアコン",image=self.aircon_img,compound="top")
        self.radio_img = Image.open("./furniture_image/radio.jpg").resize((50,50))
        self.radio_img = ImageTk.PhotoImage(self.radio_img)
        self.select_radio = ttk.Button(self,text="ラジオ",image=self.radio_img,compound="top")
        self.light_img = Image.open("./furniture_image/light.png").resize((50,50))
        self.light_img = ImageTk.PhotoImage(self.light_img)
        self.select_light = ttk.Button(self,text="照明",image=self.light_img,compound="top")
        self.other_img = Image.open("./furniture_image/other.png").resize((50,50))
        self.other_img = ImageTk.PhotoImage(self.other_img)
        self.select_other = ttk.Button(self,text="その他",image=self.other_img,compound="top")
        self.select_furniture_btns = [self.select_tv,self.select_aircon,self.select_radio,self.select_light,self.select_other]
        for i,btn in enumerate(self.select_furniture_btns):
            btn.bind("<ButtonRelease>",self.furniture_select)
            btn.config(style="Release.TButton")
            btn.place(anchor=tk.CENTER,x=170+90*i,y=150)

        self.furniture_label = tk.Label(self,text="家電選択",font=font.Font(size=15))
        self.furniture_label.place(anchor=tk.CENTER,x=350,y=90)

        self.select_tv.config(style="Select.TButton")

        self.label2 = tk.Label(self,text="赤外線登録名",font=("",13))
        self.register_name = tk.Entry(self,width=20,font=("",13))
        self.irbutton = tk.Button(self,text="リモコンボタンを押して登録",command=self.irRegister,font=font.Font(size=26))
        self.back_button = tk.Button(self,text="back",command=self.Back,font=("",13))
        self.delete_button = tk.Button(self,text="選択した項目を削除",command=self.delete,font=("",13))
        self.back_button.place(x=0,y=0)
        self.label.place(anchor=tk.CENTER,x=350,y=30)
        self.label2.place(anchor=tk.CENTER,x=180,y=240)
        self.register_name.place(anchor=tk.CENTER,x=350,y=240)
        self.irbutton.place(anchor=tk.CENTER,x=350,y=300)

        self.parent = setting_f #SettingFrame
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = (1,2)
        self.tree.column(1,width=30)
        self.tree["show"] = "headings"
        self.tree.heading(1,text="id")
        self.tree.heading(2,text="登録名")
        self.tree_update()
        self.tree.place(anchor=tk.CENTER,x=350,y=450)
        self.delete_button.place(anchor=tk.CENTER,x=350,y=600)
        
    def Start(self):
        self.tree_update()
        self.pack()
    
    def furniture_select(self,event):
        print(event)
        for i,btn in enumerate(self.select_furniture_btns):
            if event.widget == btn:
                self.furniture_name.set(self.furniture_idx2label[i])
            btn.config(style="Release.TButton")
        event.widget.config(style="Select.TButton")
        print(self.furniture_name.get())
        self.tree_update()

    def Back(self):
        self.pack_forget()
        self.parent.pack()

    def irRegister(self):
        if ir_serial == None:
            messagebox.showerror("警告","irMagicianが接続されていません。\nデバイスを接続してアプリを再起動してください。")
            return
        thread1 = threading.Thread(target=self.captureIR)
        thread1.start()
    
    #未実装
    def captureIR(self):
        name = self.register_name.get()
        if name == "":
            messagebox.showinfo("確認","登録名が入力されていません。\n登録名を入力してください。")
            return
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        for furniture in self.furniture_idx2label.values():
            cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
        cursor.execute("SELECT id,irname from {} ORDER BY id".format(self.furniture_name.get()))
        res = cursor.fetchall()
        print(res)
        yesno = False
        update_id = 0
        for data in res:
            if name == data[1]:
                update_id = data[0]
                yesno = messagebox.askyesno("確認","既に登録されている登録名です。\n現在登録されている信号を上書きして赤外線を登録しますか？")
                if not yesno:
                    return
        newWindow = CountWindow(self)
        geo = self.master.geometry()
        geo = geo.split("+")
        x = int(geo[1])+160
        y = int(geo[2])+160
        newWindow.geometry("+"+str(x)+"+"+str(y))
        newWindow.timer()
        print("Capturing IR...")
        ir_serial.write("c\r\n".encode())
        time.sleep(3.0)
        msg = ir_serial.readline()
        print(msg)
        num = re.sub("\\D","",str(msg))
        print(num)
        if num != "":
            if int(num) > 590:
                newWindow.destroy()
                messagebox.showinfo("警告","リモコンが赤外線登録に対応していないか、赤外線信号が長すぎます\nボタンを押す時間を短くして再度実行してください")
                return
        if name and not "Time Out" in str(msg):
            newWindow.register_waiting()
            try:
                self.saveIR(name,yesno,update_id)
                newWindow.destroy()
                self.tree_update()
            except ValueError as e:
                print(e)
                messagebox.showinfo("警告","予期せぬエラーが発生しました。\n再試行してください。")
                newWindow.destroy()
                return
        else:
            newWindow.destroy()
            messagebox.showinfo("確認","タイムアウトしました")

    #未実装
    def saveIR(self,name,yesno,update_id):
        print("Saving IR data to %s ..." % name)
        rawX = []
        ir_serial.write("I,1\r\n".encode())
        time.sleep(1.0)
        recNumberStr = ir_serial.readline()
        recNumber = int(recNumberStr, 16)
  
        ir_serial.write("I,6\r\n".encode())
        time.sleep(1.0)
        postScaleStr = ir_serial.readline()
        postScale = int(postScaleStr, 10)
  
        #for n in range(640):
        for n in range(recNumber):
            bank = n / 64
            pos = n % 64
            if (pos == 0):
                ir_serial.write(("b,%d\r\n" % bank).encode())
  
            ir_serial.write(("d,%d\n\r" % pos).encode())
            xStr = ir_serial.read(3) 
            xData = int(xStr, 16)
            rawX.append(xData)
  
        data = {'format':'raw', 'freq':38, 'data':rawX, 'postscale':postScale}

        print("Done !")
        print(rawX)
        rawX_str = ""
        for data in rawX:
            rawX_str += str(data)+","
        print(rawX_str)
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        try:
            for furniture in self.furniture_idx2label.values():
                cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
            if yesno:
                cursor.execute("UPDATE {} set irname=:irname,postscale=:postscale,freq=:freq,data=:data,format=:format where id = {}".format(self.furniture_name.get(),update_id),{"irname":name,"postscale":postScale,"freq":38,"data":rawX_str[:-1],"format":"raw"})
            else:
                cursor.execute("INSERT INTO {} (irname, postscale, freq, data, format) VALUES (:irname, :postscale, :freq, :data, :format)".format(self.furniture_name.get()),{"irname":name,"postscale":postScale,"freq":38,"data":rawX_str[:-1],"format":"raw"})
        except sqlite3.Error as e:
            print("sqlite3.Error occured:",e.args[0])
        
        connection.commit()
        connection.close()
        print("COMMIT!")
        res = messagebox.showinfo("確認","正常に登録されました")


    def delete(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        ret = messagebox.askyesno("確認","選択した項目を削除しますか?")
        if ret == True:
            for selected_item in selected_items:
                values = self.tree.item(selected_item,'values')
                print(values)
                dbpath = "gesture_db.sqlite"
                connection = sqlite3.connect(dbpath)
                cursor = connection.cursor()
                cursor.execute("DELETE FROM {} WHERE id = {}".format(self.furniture_name.get(),str(values[0])))
                connection.commit()
                connection.close()
                print("COMMIT!")
            messagebox.showinfo("確認","正常に削除されました")
            self.tree_update()

    def tree_update(self):
        for del_elem in self.tree.get_children():
            self.tree.delete(del_elem)
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        for furniture in self.furniture_idx2label.values():
            cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
        cursor.execute("SELECT id,irname from {} ORDER BY id".format(self.furniture_name.get()))
        res = cursor.fetchall()
        print(res)
        for data in res:
            self.tree.insert("","end",values=data)
