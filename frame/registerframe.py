import tkinter as tk
from tkinter import ttk
from tkinter import font, messagebox
import threading
import sqlite3
from PIL import Image,ImageTk

class FurnitureFrame(tk.Frame):
    def __init__(self,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=140)
        self.xf = tk.Frame(self,relief="ridge",border=2,width=500,height=130,highlightbackground="black",highlightcolor="black",highlightthickness=2,bd=0)
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
            btn.place(anchor=tk.CENTER,x=100+75*i,y=50)
            #btn.grid()
        
        self.label = tk.Label(self.xf,text="赤外線信号",font=("",13))
        self.label.place(anchor=tk.CENTER,x=150,y=100)
        self.ir_name = tk.StringVar()
        self.select_ir = ttk.Combobox(self.xf,state="readonly",textvariable=self.ir_name,values=self.get_data(load_id=False),font=("",13),height=5)
        self.select_ir.set(self.get_data(load_id=False)[0])
        self.select_ir.place(anchor=tk.CENTER,x=300,y=100)
        self.xf.place(anchor=tk.NW,relx=0.15,rely=0.05)
        self.furniture_label = tk.Label(self,text="家電&赤外線信号選択",font=("",13))
        self.furniture_label.place(anchor=tk.CENTER,x=350,y=10)
        self.select_tv.config(style="Select.TButton")
        
    
    def get_data(self,load_id=True):    
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        if load_id == True:
            cursor.execute("SELECT id,irname FROM {} ORDER BY id".format(self.furniture_name.get()))
            #cursor.execute("SELECT id,irname FROM sample ORDER BY id")
            res = cursor.fetchall()
            print(res)
            if res.__len__() != 0:
                return res
            else:
                return [('','')]
        else:
            cursor.execute("SELECT irname FROM {} ORDER BY id".format(self.furniture_name.get()))
            #cursor.execute("SELECT irname FROM sample ORDER BY id")
            res = cursor.fetchall()
            print(res)
            if res.__len__() != 0:
                return res
            else:
                return ['']
    
    def furniture_select(self,event):
        #print(event)
        for i,btn in enumerate(self.select_furniture_btns):
            if event.widget == btn:
                self.furniture_name.set(self.furniture_idx2label[i])
            btn.config(style="Release.TButton")
        event.widget.config(style="Select.TButton")
        print(self.furniture_name.get())
        self.tree_update()
        self.combobox_update()
        """self.ir_label2idx = {value:key for key,value in self.get_data(load_id=True)}
        ir_data = tuple(self.ir_label2idx.keys())
        self.select_ir.config(values=ir_data)
        #self.select_ir.config(values=self.get_data(load_id=False))
        #self.select_ir.set(self.get_data(load_id=False)[0])
        self.select_ir.set(ir_data[0])"""
    
    def combobox_update(self):
        self.ir_label2idx = {value:key for key,value in self.get_data(load_id=True)}
        ir_data = tuple(self.ir_label2idx.keys())
        self.select_ir.config(values=ir_data)
        #self.select_ir.config(values=self.get_data(load_id=False))
        #self.select_ir.set(self.get_data(load_id=False)[0])
        self.select_ir.set(ir_data[0])
    
    
    def tree_update(self):
        self.master.tree.delete((*self.master.tree.get_children()))
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        for furniture in self.furniture_idx2label.values():
            cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
        #cursor.execute("CREATE TABLE IF NOT EXISTS sample (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)")
        cursor.execute("SELECT id,irname,target_id from {} where target_id >= 0".format(self.furniture_name.get()))
        #cursor.execute("SELECT id,irname,target_id from sample where target_id >= 0")
        res = cursor.fetchall()
        #print(res)
        for data in res:
            class_id = data[2]//5
            move_id = data[2]%5
            self.master.tree.insert("","end",values=data[:-1]+(self.master.class_frame.cls_idx2label[class_id],self.master.move_frame.move_idx2label[move_id]))


class ClassFrame(tk.Frame):
    def __init__(self,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=180)
        self.xf = tk.Frame(self,relief="groove",border=2,width=550,height=170,highlightbackground="red",highlightcolor="red",highlightthickness=2,bd=0)
        
        self.class_name = tk.StringVar(value="zero")
        self.cls_label2idx = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"three_v2":6,"fit":7,"fox":8,"ok":9,"go":10,"little_finger":11}
        self.cls_idx2label = {value:key for key,value in self.cls_label2idx.items()}
        self.img = Image.open("./gesture_image/zero.png").resize((35,35))
        self.img = ImageTk.PhotoImage(self.img)
        self.select_zero = ttk.Button(self.xf,text="zero",image=self.img,compound="top",width=7)
        self.one_img = Image.open("./gesture_image/one.png").resize((35,35))
        self.one_img = ImageTk.PhotoImage(self.one_img)
        self.select_one = ttk.Button(self.xf,text="one",image=self.one_img,compound="top",width=7)
        self.two_img = Image.open("./gesture_image/two.png").resize((35,35))
        self.two_img = ImageTk.PhotoImage(self.two_img)
        self.select_two = ttk.Button(self.xf,text="two",image=self.two_img,compound="top",width=7)
        self.three_img = Image.open("./gesture_image/three.png").resize((35,35))
        self.three_img = ImageTk.PhotoImage(self.three_img)
        self.select_three = ttk.Button(self.xf,text="three",image=self.three_img,compound="top",width=7)
        self.four_img = Image.open("./gesture_image/four.png").resize((35,35))
        self.four_img = ImageTk.PhotoImage(self.four_img)
        self.select_four = ttk.Button(self.xf,text="four",image=self.four_img,compound="top",width=7)
        self.five_img = Image.open("./gesture_image/five.png").resize((35,35))
        self.five_img = ImageTk.PhotoImage(self.five_img)
        self.select_five = ttk.Button(self.xf,text="five",image=self.five_img,compound="top",width=7)
        self.three_v2_img = Image.open("./gesture_image/three_v2.png").resize((35,35))
        self.three_v2_img = ImageTk.PhotoImage(self.three_v2_img)
        self.select_three_v2 = ttk.Button(self.xf,text="three v2",image=self.three_v2_img,compound="top",width=7)
        self.fit_img = Image.open("./gesture_image/fit.png").resize((35,35))
        self.fit_img = ImageTk.PhotoImage(self.fit_img)
        self.select_fit = ttk.Button(self.xf,text="fit",image=self.fit_img,compound="top",width=7)
        self.fox_img = Image.open("./gesture_image/fox.png").resize((35,35))
        self.fox_img = ImageTk.PhotoImage(self.fox_img)
        self.select_fox = ttk.Button(self.xf,text="fox",image=self.fox_img,compound="top",width=7)
        self.ok_img = Image.open("./gesture_image/ok.png").resize((35,35))
        self.ok_img = ImageTk.PhotoImage(self.ok_img)
        self.select_ok = ttk.Button(self.xf,text="ok",image=self.ok_img,compound="top",width=7)
        self.go_img = Image.open("./gesture_image/go.png").resize((35,35))
        self.go_img = ImageTk.PhotoImage(self.go_img)
        self.select_go = ttk.Button(self.xf,text="go",image=self.go_img,compound="top",width=7)
        self.little_finger_img = Image.open("./gesture_image/little_finger.png").resize((35,35))
        self.little_finger_img = ImageTk.PhotoImage(self.little_finger_img)
        self.select_little_finger = ttk.Button(self.xf,text="little fin",image=self.little_finger_img,compound="top",width=7)
        self.select_class_btns = [self.select_zero,self.select_one,self.select_two,self.select_three,self.select_four,self.select_five,
                                self.select_three_v2,self.select_fit,self.select_fox,self.select_ok,self.select_go,self.select_little_finger]
        for i,btn in enumerate(self.select_class_btns[:6]):
            btn.bind("<ButtonRelease>",self.class_select)
            btn.config(style="Release.TButton")
            btn.place(anchor=tk.CENTER,x=85+75*i,y=50)
            #btn.place(anchor=tk.CENTER,x=str(3+2*i)+"cm",y=str(2.5)+"cm")
        for i,btn in enumerate(self.select_class_btns[6:]):
            btn.bind("<ButtonRelease>",self.class_select)
            btn.config(style="Release.TButton")
            btn.place(anchor=tk.CENTER,x=85+75*i,y=120)
            #btn.place(anchor=tk.CENTER,x=str(3+2*i)+"cm",y=str(5)+"cm")
        self.select_zero.config(style="Select.TButton")
        self.xf.place(anchor=tk.NW,relx=0.11,rely=0.05)
        self.class_label = tk.Label(self,text="ジェスチャ選択",font=("",13))#font.Font(size=15))
        self.class_label.place(anchor=tk.CENTER,x=350,y=10)
        
        
    def class_select(self,event):
        for i,btn in enumerate(self.select_class_btns):
            if event.widget == btn:
                self.master.update_move_img(i)
                self.class_name.set(self.cls_idx2label[i])
                for j,btn2 in enumerate(self.master.move_frame.select_move_btns):
                    btn2.config(image=self.master.move_img_list[j])
                    
                continue
            btn.config(style="Release.TButton")
        print(event.widget == self.select_zero)
        event.widget.config(style="Select.TButton")


class MoveFrame(tk.Frame):
    def __init__(self,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=110)
        self.xf = tk.Frame(self,relief="groove",border=2,width=500,height=100,highlightbackground="blue",highlightcolor="blue",highlightthickness=2,bd=0)
        
        self.move_name = tk.StringVar(value="stop")
        self.move_label2idx = {"stop":0,"up":1,"down":2,"right":3,"left":4}
        self.move_idx2label = {value:key for key,value in self.move_label2idx.items()}
        self.update_move_img(0)
        self.select_stop = ttk.Button(self.xf,text="stop",image=self.move_img_list[0],compound="top",width=7)
        self.select_up = ttk.Button(self.xf,text="up",image=self.move_img_list[1],compound="top",width=7)
        self.select_down = ttk.Button(self.xf,text="down",image=self.move_img_list[2],compound="top",width=7)
        self.select_right = ttk.Button(self.xf,text="right",image=self.move_img_list[3],compound="top",width=7)
        self.select_left = ttk.Button(self.xf,text="left",image=self.move_img_list[4],compound="top",width=7)
        self.select_move_btns = [self.select_stop,self.select_up,self.select_down,self.select_right,self.select_left]
        for i,btn in enumerate(self.select_move_btns):
            btn.bind("<ButtonRelease>",self.move_select)
            btn.config(style="Release.TButton")
            btn.place(anchor=tk.CENTER,x=95+75*i,y=50)
            #btn.place(anchor=tk.CENTER,x=str(3+2.5*i)+"cm",y=str(7.5)+"cm")
        self.xf.place(anchor=tk.NW,relx=0.15,rely=0.05)
        self.move_label = tk.Label(self,text="動作選択",font=("",13))#font.Font(size=15))
        self.move_label.place(anchor=tk.CENTER,x=350,y=10)
        self.select_stop.config(style="Select.TButton")
            
    
    def update_move_img(self,num):
        clsname = self.master.class_frame.cls_idx2label[num]
        self.stop_img = Image.open("./gesture_image/"+clsname+".png").resize((35,35))
        self.stop_img = ImageTk.PhotoImage(self.stop_img)
        self.up_img = Image.open("./gesture_image/"+clsname+"_up.png").resize((35,35))
        self.up_img = ImageTk.PhotoImage(self.up_img)
        self.down_img = Image.open("./gesture_image/"+clsname+"_down.png").resize((35,35))
        self.down_img = ImageTk.PhotoImage(self.down_img)
        self.right_img = Image.open("./gesture_image/"+clsname+"_right.png").resize((35,35))
        self.right_img = ImageTk.PhotoImage(self.right_img)
        self.left_img = Image.open("./gesture_image/"+clsname+"_left.png").resize((35,35))
        self.left_img = ImageTk.PhotoImage(self.left_img)
        self.move_img_list = [self.stop_img,self.up_img,self.down_img,self.right_img,self.left_img]

    def move_select(self,event):
        for i,btn in enumerate(self.select_move_btns):
            if event.widget == btn:
                self.move_name.set(self.move_idx2label[i])
                continue
            btn.config(style="Release.TButton")
        event.widget.config(style="Select.TButton")

        
class RegisterFrame(tk.Frame):
    def __init__(self,setting_f,master=None,**kwargs):
        tk.Frame.__init__(self,master=master,**kwargs,width=700,height=700)
        self.tree = ttk.Treeview(self,height=5)
        self.tree["columns"] = (1,2,3,4)
        self.tree.column(1,width=30)
        self.tree["show"] = "headings"
        self.tree.heading(1,text="id")
        self.tree.heading(2,text="赤外線信号")
        self.tree.heading(3,text="ジェスチャ")
        self.tree.heading(4,text="動作")
        self.style = ttk.Style()
        self.style.configure("Treeview",font=("",13))
        self.style.configure("Treeview.Heading",font=("",13))
        self.label = tk.Label(self,text="ジェスチャ登録",font=font.Font(size=30))
        #self.class_name = tk.StringVar(value="zero")
        #self.move_name = tk.StringVar(value="stop")
        #self.ir_name = tk.StringVar()
        #self.cls_label2idx = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"three_v2":6,"fit":7,"fox":8,"ok":9,"go":10,"little_finger":11}
        #self.move_label2idx = {"stop":0,"up":1,"down":2,"right":3,"left":4}
        #self.cls_idx2label = {value:key for key,value in self.cls_label2idx.items()}
        #self.move_idx2label = {value:key for key,value in self.move_label2idx.items()}
        self.furniture_frame = FurnitureFrame(self)
        self.furniture_frame.place(anchor=tk.CENTER,x=350,y=130)
        self.class_frame = ClassFrame(self)
        self.class_frame.place(anchor=tk.CENTER,x=350,y=290)
        self.move_frame = MoveFrame(self)
        self.move_frame.place(anchor=tk.CENTER,x=350,y=440)

        
        """self.s2 = ttk.Style()
        self.s2.configure("Release.TButton",font=("",13))
        self.s = ttk.Style()
        self.s.theme_use('default')
        #self.s.configure("Select.TButton",background='#87cefa',foreground='red')
        self.s.configure("Select.TButton",background='#87cefa',foreground='red',font=("",12,"bold"))"""
        
        #self.select_tv.config(style="Select.TButton")
        #self.select_zero.config(style="Select.TButton")
        #self.select_stop.config(style="Select.TButton")
        

        #self.select_ir = ttk.Combobox(self,state="readonly",textvariable=self.ir_name,values=self.get_data(load_id=False))
        #self.select_ir.set(self.get_data(load_id=False)[0])
        self.register_button = tk.Button(self,text="登録",font=font.Font(size=26),command=self.Register)
        self.back_button = tk.Button(self,text="back",font=font.Font(size=13),command=self.Back)
        self.delete_button = tk.Button(self,text="選択した項目を削除",font=font.Font(size=13),command=self.delete)
        self.label.place(anchor=tk.CENTER,x=350,y=30)
        #self.select_ir.place(anchor=tk.CENTER,x=350,y=160)
        self.register_button.place(anchor=tk.CENTER,x=350,y=520)
        self.back_button.place(x=0,y=0)
        self.parent = setting_f #SettingFrame
        #print(self.ir_label2idx)
        self.furniture_frame.tree_update()
        self.tree.place(anchor=tk.CENTER,x=350,y=610)
        self.delete_button.place(anchor=tk.CENTER,x=350,y=685) 
        #self.pack()
    
    def Start(self):
        self.furniture_frame.tree_update()
        self.furniture_frame.combobox_update()
        self.pack()
    
    def update_move_img(self,num):
        clsname = self.class_frame.cls_idx2label[num]
        self.stop_img = Image.open("./gesture_image/"+clsname+".png").resize((35,35))
        self.stop_img = ImageTk.PhotoImage(self.stop_img)
        self.up_img = Image.open("./gesture_image/"+clsname+"_up.png").resize((35,35))
        self.up_img = ImageTk.PhotoImage(self.up_img)
        self.down_img = Image.open("./gesture_image/"+clsname+"_down.png").resize((35,35))
        self.down_img = ImageTk.PhotoImage(self.down_img)
        self.right_img = Image.open("./gesture_image/"+clsname+"_right.png").resize((35,35))
        self.right_img = ImageTk.PhotoImage(self.right_img)
        self.left_img = Image.open("./gesture_image/"+clsname+"_left.png").resize((35,35))
        self.left_img = ImageTk.PhotoImage(self.left_img)
        self.move_img_list = [self.stop_img,self.up_img,self.down_img,self.right_img,self.left_img]
    
    
    def Register(self):
        #ここで所定の登録作業を実行する
        thread1 = threading.Thread(target=self.thread_register)
        thread1.start()
    
    def thread_register(self):
        target_id = 5*self.class_frame.cls_label2idx[self.class_frame.class_name.get()]+self.move_frame.move_label2idx[self.move_frame.move_name.get()]
        pkey_id = self.furniture_frame.ir_label2idx[self.furniture_frame.ir_name.get()]
        print("ir_name:",self.furniture_frame.ir_name.get())
        if self.furniture_frame.ir_name.get() == "":
            messagebox.showinfo("確認","赤外線信号が登録されていません。\n赤外線登録画面から赤外線を登録してください。")
            return
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        try:
            for furniture in self.furniture_frame.furniture_idx2label.values():
                cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
            #cursor.execute("CREATE TABLE IF NOT EXISTS sample (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)")
            #cursor.execute("UPDATE sample SET target_id = null where target_id = :target_id",{"id":pkey_id,"target_id":target_id})
            cursor.execute("UPDATE {} SET target_id = null where target_id = :target_id".format(self.furniture_frame.furniture_name.get()),{"id":pkey_id,"target_id":target_id})
            #cursor.execute("UPDATE sample SET target_id = :target_id where id = :id",{"id":pkey_id,"target_id":target_id})
            cursor.execute("UPDATE {} SET target_id = :target_id where id = :id".format(self.furniture_frame.furniture_name.get()),{"id":pkey_id,"target_id":target_id})
        except sqlite3.Error as e:
            print("sqlite3.Error occured:",e.args[0])
        
        connection.commit()
        connection.close()
        print("COMMIT!")
        print(self.class_frame.class_name.get(),self.move_frame.move_name.get())
        messagebox.showinfo("確認","正常に登録されました")
        self.furniture_frame.tree_update()
        

    def Back(self):
        self.pack_forget()
        self.parent.pack()

    
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
                #cursor.execute("UPDATE sample SET target_id = null WHERE id = "+str(values[0]))
                cursor.execute("UPDATE {} SET target_id = null WHERE id = {}".format(self.furniture_frame.furniture_name.get(),str(values[0])))
                connection.commit()
                connection.close()
                print("COMMIT!")
            messagebox.showinfo("確認","正常に削除されました")
            self.furniture_frame.tree_update()

            
    """def get_data(self,load_id=True):    
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        if load_id == True:
            cursor.execute("SELECT id,irname FROM {} ORDER BY id".format(self.furniture_name.get()))
            #cursor.execute("SELECT id,irname FROM sample ORDER BY id")
            res = cursor.fetchall()
            print(res)
            if res.__len__() != 0:
                return res
            else:
                return [('','')]
        else:
            cursor.execute("SELECT irname FROM {} ORDER BY id".format(self.furniture_name.get()))
            #cursor.execute("SELECT irname FROM sample ORDER BY id")
            res = cursor.fetchall()
            print(res)
            if res.__len__() != 0:
                return res
            else:
                return ['']"""

    """def tree_update(self):
        self.tree.delete((*self.tree.get_children()))
        dbpath = "gesture_db.sqlite"
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        for furniture in self.furniture_frame.furniture_idx2label.values():
            cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)".format(furniture))
        #cursor.execute("CREATE TABLE IF NOT EXISTS sample (id INTEGER PRIMARY KEY, irname TEXT,postscale INTEGER, freq INTEGER, data TEXT,format TEXT,target_id INTEGER)")
        cursor.execute("SELECT id,irname,target_id from {} where target_id >= 0".format(self.furniture_frame.furniture_name.get()))
        #cursor.execute("SELECT id,irname,target_id from sample where target_id >= 0")
        res = cursor.fetchall()
        #print(res)
        for data in res:
            class_id = data[2]//5
            move_id = data[2]%5
            self.tree.insert("","end",values=data[:-1]+(self.cls_idx2label[class_id],self.move_idx2label[move_id]))"""