import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import configparser

class EnvironmentFrame(tk.Frame):
    def __init__(self,setting_f,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=700)
        config_dict = self.Read_Config()
        self.label = tk.Label(self,text="環境設定",font=font.Font(size=30))
        self.back_button = tk.Button(self,text="back",command=self.Back,font=("",13))
        self.label_camera_view = tk.Label(self,text="ジェスチャ認識画面でカメラビューを表示する",font=("",13))
        self.select_camera_view = tk.IntVar()
        self.select_camera_view.set(config_dict["camera_view"])
        self.yes_camera_view = tk.Radiobutton(self,text="yes",value=1,variable=self.select_camera_view,font=("",13))
        self.no_camera_view = tk.Radiobutton(self,text="no",value=0,variable=self.select_camera_view,font=("",13))
        
        self.label_sound_support = tk.Label(self,text="ジェスチャ認識時に音声サポートを使用する",font=("",13))
        self.select_sound_support = tk.IntVar()
        self.select_sound_support.set(config_dict["sound_support"])
        self.yes_sound_support = tk.Radiobutton(self,text="yes",value=1,variable=self.select_sound_support,font=("",13))
        self.no_sound_support = tk.Radiobutton(self,text="no",value=0,variable=self.select_sound_support,font=("",13))
        self.label.place(anchor=tk.CENTER,x=350,y=30)
        self.label_camera_view.place(anchor=tk.CENTER,x=260,y=150)
        self.yes_camera_view.place(anchor=tk.CENTER,x=460,y=150)
        self.no_camera_view.place(anchor=tk.CENTER,x=510,y=150)
        self.label_sound_support.place(anchor=tk.CENTER,x=255,y=250)
        self.yes_sound_support.place(anchor=tk.CENTER,x=460,y=250)
        self.no_sound_support.place(anchor=tk.CENTER,x=510,y=250)

        self.apply_button = tk.Button(self,text="設定を変更",font=("",26),command=self.Apply)
        self.apply_button.place(anchor=tk.CENTER,x=350,y=600)
        self.back_button.place(x=0,y=0)
        self.parent = setting_f #SettingFrame

    def Start(self):
        config_dict = self.Read_Config()
        self.select_camera_view.set(config_dict["camera_view"])
        self.select_sound_support.set(config_dict["sound_support"])
        self.pack()

    def Back(self):
        self.pack_forget()
        self.parent.pack()
    
    def Read_Config(self):
        config = configparser.ConfigParser()
        config.read("./config/config.ini")

        section1 = "exec"
        config_dict = {}
        config_dict["camera_view"] = config.get(section1,"camera_view")
        config_dict["sound_support"] = config.get(section1,"sound_support")
        return config_dict



    def Apply(self):
        res = messagebox.askyesno("確認","設定を変更しますか？")
        if res:
            camera_view = self.select_camera_view.get()
            print(self.select_camera_view.get())
            sound_support = self.select_sound_support.get()
            if camera_view == 1:
                print("camera view ON")
            else:
                print("camera view OFF")
            
            if sound_support == 1:
                print("sound support ON")
            else:
                print("sound support OFF")
            
            config = configparser.RawConfigParser()

            section1 = "exec"
            config.add_section(section1)
            config.set(section1,"camera_view",camera_view)
            config.set(section1,"sound_support",sound_support)

            with open("./config/config.ini","w") as f:
                config.write(f)
        

