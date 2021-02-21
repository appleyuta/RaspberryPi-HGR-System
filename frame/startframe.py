import tkinter as tk
from tkinter import font
import threading
from settingframe import SettingFrame
from execframe import ExecuteFrame
from serial_device import ir_serial
from PIL import Image,ImageTk


class StartFrame(tk.Frame):
    def __init__(self,master=None,**kwargs):
        tk.Frame.__init__(self,master,**kwargs,width=700,height=700)
        self.label = tk.Label(self,text="Gesture Recognition System",font=font.Font(family ="Times",size=35))
        self.start_button = tk.Button(self,text="Start",font=font.Font(size=45),height=2,command=self.Start)
        #self.set_img = Image.open("./image/setting.png").resize((60,60))
        #self.set_img = ImageTk.PhotoImage(self.set_img)
        self.set_button = tk.Button(self,text="Setting",font=font.Font(size=45),height=2,command=self.Setting)
        self.label.place(anchor=tk.CENTER,x=350,y=30)
        self.start_button.place(anchor=tk.CENTER,x=350,y=250,width=270,height=200)
        self.set_button.place(anchor=tk.CENTER,x=350,y=450,width=270,height=200)
        self.e_frame = ExecuteFrame(self)
        self.set_frame = SettingFrame(start_f=self)
        
    #ジェスチャ認識を実行
    def Start(self):
        self.pack_forget()
        if ir_serial == None:
            threading.Thread(target=tk.messagebox.showerror,args=("警告","irMagicianが接続されていないか、認識されていません。\nデバイスを再接続してください。")).start()
        print("Button is clicked.")
        #thread1 = threading.Thread(target=ExecuteFrame,args=(self,))
        #thread1.start()
        self.e_frame.set_config()
        threading.Thread(target=self.e_frame.Start).start()
    
    #設定画面へ移行
    def Setting(self):
        print("setting")
        self.pack_forget()
        #SettingFrame(start_f=self)
        threading.Thread(target=self.set_frame.Start).start()
