import tkinter as tk
from tkinter import font
from registerframe import RegisterFrame
from envframe import EnvironmentFrame
from infraredregisterframe import InfraredSignalRegisterFrame
import threading
from PIL import Image,ImageTk

class SettingFrame(tk.Frame):
    def __init__(self,start_f,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=700)
        self.back_button = tk.Button(self,text="back menu",font=font.Font(size=13),command=self.Back)
        self.ir_img = Image.open("./image/ir.png").resize((50,50))
        self.ir_img = ImageTk.PhotoImage(self.ir_img)
        self.infrared_register_button = tk.Button(self,text="赤外線登録",image=self.ir_img,font=font.Font(size=40),command=self.InfraredSignalRegister,compound="left")
        self.gesture_img = Image.open("./gesture_image/zero.png").resize((50,50))
        self.gesture_img = ImageTk.PhotoImage(self.gesture_img)
        self.register_button = tk.Button(self,text="ジェスチャ登録",image=self.gesture_img,font=font.Font(size=40),command=self.Register,compound="left")
        self.env_img = Image.open("./image/envsetting.png").resize((50,50))
        self.env_img = ImageTk.PhotoImage(self.env_img)
        self.env_button = tk.Button(self,text="環境設定",image=self.env_img,font=font.Font(size=40),command=self.Environment,compound="left")
        self.back_button.place(x=0,y=0)
        self.infrared_register_button.place(anchor=tk.CENTER,x=350,y=200,width=450,height=150)
        self.register_button.place(anchor=tk.CENTER,x=350,y=350,width=450,height=150)
        self.env_button.place(anchor=tk.CENTER,x=350,y=500,width=450,height=150)
        self.parent = start_f #StratFrame
        self.ir_frame = InfraredSignalRegisterFrame(setting_f=self)
        self.register_frame = RegisterFrame(setting_f=self)
        self.env_frame = EnvironmentFrame(setting_f=self)
        #self.pack()
    
    def Start(self):
        self.pack()
        
    #ホーム画面へ移行
    def Back(self):
        self.pack_forget()
        self.parent.pack()
        
    def InfraredSignalRegister(self):
        self.pack_forget()
        #threading.Thread(target=InfraredSignalRegisterFrame,args=(self,)).start()
        threading.Thread(target=self.ir_frame.Start).start()
        
    #ジェスチャ登録画面へ移行
    def Register(self):
        self.pack_forget()
        #threading.Thread(target=RegisterFrame,args=(self,)).start()
        threading.Thread(target=self.register_frame.Start).start()
        
    #環境設定画面へ移行
    def Environment(self):
        self.pack_forget()
        #threading.Thread(target=EnvironmentFrame,args=(self,)).start()
        threading.Thread(target=self.env_frame.Start).start()
