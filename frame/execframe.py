import tkinter as tk
from tkinter import ttk
from tkinter import font
from PIL import Image,ImageTk
from yolo_tflite import yolo_obj
import sqlite3
import configparser
import os

class FurnitureFrame(tk.Frame):
    def __init__(self,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=110)
        self.xf = tk.Frame(self,relief="ridge",border=2,width=500,height=100,highlightbackground="black",highlightcolor="black",highlightthickness=2,bd=0)
        self.furniture_idx2label = {0:"tv",1:"aircon",2:"radio",3:"light",4:"other"}
        self.furniture_name = tk.StringVar(value="tv")
        self.ir_label2idx = {value:key for key,value in self.get_data(load_id=True)}
        self.tv_img = Image.open("./furniture_image/tv.png").resize((35,35))
        self.tv_img = ImageTk.PhotoImage(self.tv_img)
        self.select_tv = ttk.Button(self.xf,text="テレビ",image=self.tv_img,compound="top",width=7)
        self.aircon_img = Image.open("./furniture_image/aircon.png").resize((35,35))
        self.aircon_img = ImageTk.PhotoImage(self.aircon_img)
        self.select_aircon = ttk.Button(self.xf,text="エアコン",image=self.aircon_img,compound="top",width=7)
        self.radio_img = Image.open("./furniture_image/radio.jpg").resize((35,35))
        self.radio_img = ImageTk.PhotoImage(self.radio_img)
        self.select_radio = ttk.Button(self.xf,text="ラジオ",image=self.radio_img,compound="top",width=7)
        self.light_img = Image.open("./furniture_image/light.png").resize((35,35))
        self.light_img = ImageTk.PhotoImage(self.light_img)
        self.select_light = ttk.Button(self.xf,text="照明",image=self.light_img,compound="top",width=7)
        self.other_img = Image.open("./furniture_image/other.png").resize((35,35))
        self.other_img = ImageTk.PhotoImage(self.other_img)
        self.select_other = ttk.Button(self.xf,text="その他",image=self.other_img,compound="top",width=7)
        self.select_furniture_btns = [self.select_tv,self.select_aircon,self.select_radio,self.select_light,self.select_other]
        for i,btn in enumerate(self.select_furniture_btns):
            btn.bind("<ButtonRelease>",self.furniture_select)
            btn.config(style="Release.TButton")
            btn.place(anchor=tk.CENTER,x=95+75*i,y=50)
            
        self.xf.place(anchor=tk.NW,relx=0.15,rely=0.05)
        self.furniture_label = tk.Label(self,text="家電選択",font=("",13))
        self.furniture_label.place(anchor=tk.CENTER,x=350,y=10)
        self.select_tv.config(style="Select.TButton")
        
    
    def get_data(self,load_id=True):    
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        if load_id == True:
            for furniture in self.furniture_idx2label.values():
                cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
            cursor.execute("SELECT id,irname FROM {} ORDER BY id".format(self.furniture_name.get()))
            res = cursor.fetchall()
            print(res)
            if res.__len__() != 0:
                return res
            else:
                return [('','')]
        else:
            cursor.execute("SELECT irname FROM {} ORDER BY id".format(self.furniture_name.get()))
            res = cursor.fetchall()
            print(res)
            if res.__len__() != 0:
                return res
            else:
                return ['']
    
    def furniture_select(self,event):
        for i,btn in enumerate(self.select_furniture_btns):
            if event.widget == btn:
                self.furniture_name.set(self.furniture_idx2label[i])
            btn.config(style="Release.TButton")
        event.widget.config(style="Select.TButton")
        print(self.furniture_name.get())
        self.master.model.set_furniture(self.furniture_name.get())
        self.tree_update()
        
    def tree_update(self):
        for del_elem in self.master.tree.get_children():
            self.master.tree.delete(del_elem)
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        for furniture in self.furniture_idx2label.values():
            cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
        cursor.execute("SELECT id,irname,target_id from {} where target_id >= 0".format(self.furniture_name.get()))
        res = cursor.fetchall()
        for data in res:
            class_id = data[2]//5
            move_id = data[2]%5
            self.master.tree.insert("","end",values=data[:-1]+(self.master.cls_idx2label[class_id],self.master.move_idx2label[move_id]))


class ExecuteFrame(tk.Frame):
    def __init__(self,start_f,master=None,**kwargs):
        tk.Frame.__init__(self,master,**kwargs,width=700,height=700)
        self.canvas = tk.Canvas(self,width=600,height=400)
        self.canvas.place(anchor=tk.CENTER,x=350,y=200)
        self.tree = ttk.Treeview(self,height=5)
        self.tree["columns"] = (1,2,3,4)
        self.tree.column(1,width=30)
        self.tree["show"] = "headings"
        self.tree.heading(1,text="id")
        self.tree.heading(2,text="赤外線信号")
        self.tree.heading(3,text="ジェスチャ")
        self.tree.heading(4,text="動作")
        
        self.button = tk.Button(self,text="Stop",font=font.Font(size=26),command=self.Stop)
        
        self.furniture_frame = FurnitureFrame(self)
        self.furniture_frame.place(anchor=tk.CENTER,x=350,y=450)

        self.cls_label2idx = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"three_v2":6,"fit":7,"fox":8,"ok":9,"go":10,"little_finger":11}
        self.move_label2idx = {"stop":0,"up":1,"down":2,"right":3,"left":4}
        self.cls_idx2label = {value:key for key,value in self.cls_label2idx.items()}
        self.move_idx2label = {value:key for key,value in self.move_label2idx.items()}
        
        self.furniture_frame.tree_update()
        self.tree.place(anchor=tk.CENTER,x=350,y=570)
        self.button.place(anchor=tk.CENTER,x=350,y=660)
        
        self.parent = start_f #StartFrame
        self.model = yolo_obj
        self.model.set_exec_f(self)
        self.model.set_furniture(self.furniture_frame.furniture_name.get())
        self.set_config()
        self.checker = None
        
    def create_config(self):
        config = configparser.RawConfigParser()
        section1 = "exec"
        config.add_section(section1)
        config.set(section1,"camera_view",1)
        config.set(section1,"sound_support",1)
        with open("./config/config.ini","w") as f:
            config.write(f)

    def set_config(self):
        if not os.path.isdir("./config"):
            os.mkdir("./config")
        if not os.path.exists("./config/config.ini"):
            self.create_config()
        
        config = configparser.SafeConfigParser()
        config.read("./config/config.ini")

        section1 = "exec"
        if not config.has_section(section1):
            self.create_config()
            config.read("./config/config.ini")
        if not (config.has_option(section1,"camera_view") and config.has_option(section1,"sound_support")):
            self.create_config()
            config.read("./config/config.ini")
        self.model.use_camera = int(config.get(section1,"camera_view"))
        self.model.use_sound = int(config.get(section1,"sound_support"))
        
    def Back(self):
        self.pack_forget()
        self.parent.pack()
    
    def Start(self):
        self.furniture_frame.tree_update()
        self.pack()
        self.model.stop = False
        self.model.exec_model()
        

    def Stop(self):
        if self.model != None:
            self.model.stop = True
        self.pack_forget()
        self.parent.pack()
    
    def update(self):
        if self.checker != self.model.img:
            self.canvas.create_image((0,0),image=self.model.img,anchor=tk.NW,tag="img")
            self.checker = self.model.img
        else:
            pass
        self.after(1,self.update)
