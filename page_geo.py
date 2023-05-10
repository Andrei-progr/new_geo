import os
import customtkinter as ctk
from tkinter import ttk
import numpy as np
import tkinter as tk
from PIL import Image, ImageOps, ImageTk
import cv2
from photo_editor import ImagePrediction
from tkinter import ttk

home_color = "#f5f2ff"
nav_color = "#c6c6ff"
import json
btn_color = "#6fe8a4"


class GeoColumn:
    def __init__(self, parent, model, project_id, well_id, img_name):
        self.model = model
        self.parent = parent
        self.img_name = img_name
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color=home_color)
        self.current_button = 0
        self.project_id = project_id
        self.well_id = well_id
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        # s = img_name
        # s = s[::-1]
        # pos = s.find('/')
        # s = s[:pos]
        # s = s[::-1]
        # self.file_path = os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + project_id + "\\" + well_id + "\\" + s
        ### Деление фото на колонки
        self.model.clear(self.file_path + "\\column\\clear\\")
        image = Image.open(self.img_name)
        b, g, r = image.split()
        self.img = Image.merge("RGB", (r, g, b))
        self.imageMask = ImagePrediction(self.img)
        self.columns = self.imageMask.PredictColumns()
        self.imageMask.DivideColumns(self.img, self.file_path + "\\column\\clear\\")
        ### Загрузка колонок
        self.column_dir = self.model.load_columns(self.file_path + "\\column\\clear\\")

        self.button_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#F5FFFA")
        self.button_frame.place(relwidth=0.1, relheight=0.5, relx=0.02, rely=0.1)
        self.lbl1 = ctk.CTkLabel(self.button_frame, text="Выберите \n изображение", text_color="grey50")
        self.lbl1.place(relwidth=1, relheight=0.2, relx=0, rely=0)

        self.btn_names = ['целиком']
        for i in self.column_dir:
            self.btn_names.append(i)

        def create_pic_btn(name):
            return ctk.CTkButton(self.button_frame, font=("Arial", 12),
                                 text=name, text_color="grey25", fg_color="#F5FFFA", hover_color="#6cdfff",
                                 image=self.model.z, anchor="w", command=lambda: self.review_column(name))

        self.btns = {}
        counter = 0
        for i in self.btn_names:
            self.btns[i] = create_pic_btn(i)
            self.btns[i].place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.2 + 0.1 * counter)
            counter += 1

        self.btns['целиком'].configure(fg_color="#6cdfff", text_color="black")
        self.current_button = self.column_dir[0]

        self.frames = {}
        for i in self.btn_names:
            if i == 'целиком':
                f = FullFoto(self.frame, self.model, self.img_name, project_id, well_id)
                self.frames[i] = f
            else:
                f = ColumnFrame(self.frame, self.model, i, project_id, well_id)
                self.frames[i] = f
        print(self.frames)
        self.predict = ctk.CTkButton(self.frame, text="Предсказать", command = lambda: self.to_predict())
        self.predict.configure(fg_color="#6fe8a4", text_color="black")
        self.predict.place(relwidth=0.2, relheight=0.06, relx=0.68, rely=0.78)

        self.save_pr = ctk.CTkButton(self.frame, text="сохранить")
        self.save_pr.configure(fg_color="#6cdfff", text_color="black")
        self.save_pr.place(relwidth=0.2, relheight=0.06, relx=0.02, rely=0.92)

        self.btn1 = ctk.CTkButton(self.frame, text="Разрушенный")
        self.btn1.configure(fg_color="grey75", text_color="black")
        self.btn1.place(relwidth=0.08, relheight=0.06, relx=0.6, rely=0.68)

        self.btn2 = ctk.CTkButton(self.frame, text="Прожилки")
        self.btn2.configure(fg_color="grey75", text_color="black")
        self.btn2.place(relwidth=0.08, relheight=0.06, relx=0.7, rely=0.68)

        self.btn3 = ctk.CTkButton(self.frame, text="Трещины")
        self.btn3.configure(fg_color="grey75", text_color="black")
        self.btn3.place(relwidth=0.08, relheight=0.06, relx=0.8, rely=0.68)

        self.btn4 = ctk.CTkButton(self.frame, text="Порода")
        self.btn4.configure(fg_color="grey75", text_color="black")
        self.btn4.place(relwidth=0.08, relheight=0.06, relx=0.9, rely=0.68)

        self.review_column('целиком')


    def review_column(self, name):
        for j in self.btn_names:
            self.btns[j].configure(fg_color="#6cdfff" if j == name else "#F5FFFA")
        if self.current_button == name:
            pass
        else:
            self.frames[self.current_button].frame.place_forget()
            self.frames[self.current_button].table.place_forget()
            self.current_button = name
            if name == 'целиком':
                self.frames[name].frame.place(relwidth=0.45, relheight=0.75, relx=0.14, rely=0.1)
                self.frames[name].table.place(relwidth=0.35, relheight=0.5, relx=0.6, rely=0.1)
            else:
                self.frames[name].frame.place(relwidth=0.32, relheight=0.75, relx=0.14, rely=0.1)
                self.frames[name].table.place(relwidth=0.45, relheight=0.5, relx=0.5, rely=0.1)


    def to_predict(self):
        methods = [self.imageMask.PredictDestroyed, self.imageMask.PredictProzhilki, self.imageMask.PredictPoroda]
        paths = ['destroyed', 'prozhilki', 'poroda']
        colors = ([0,150,150], [85, 210, 0], [200, 150, 50])
        for k in range(len(methods)):
            mask = methods[k]()
            img = cv2.resize(self.imageMask.img, (mask.shape[1], mask.shape[0]),
                                        interpolation=cv2.INTER_AREA)
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    if mask[i, j] >= 125:
                        img[i, j] = colors[k]
            cv2.imwrite(self.file_path + "\\column\\" + paths[k] + "\\mask.png", img)
            self.model.clear(self.file_path + "\\column\\" + paths[k] + "\\columns\\")
            self.imageMask.DivideColumns(img, self.file_path + "\\column\\" + paths[k] + "\\columns\\")

        self.btn1.configure(fg_color="#F5FFFA", command=lambda: self.change_type('destroyed'))
        self.btn2.configure(fg_color="#F5FFFA", command=lambda: self.change_type('prozhilki'))
        self.btn3.configure(fg_color="#F5FFFA", command=lambda: self.change_type('treshini'))
        self.btn4.configure(fg_color="#F5FFFA", command=lambda: self.change_type('poroda'))
        self.predict.configure(fg_color = "grey75")

        self.change_type('destroyed')

    def change_type(self, type):
        self.btn1.configure(fg_color = "#6cdfff" if type == 'destroyed' else "#F5FFFA")
        self.btn2.configure(fg_color = "#6cdfff" if type == 'prozhilki' else "#F5FFFA")
        self.btn3.configure(fg_color = "#6cdfff" if type == 'treshini' else "#F5FFFA")
        self.btn4.configure(fg_color = "#6cdfff" if type == 'poroda' else "#F5FFFA")
        path = self.file_path + "\\column\\" + type + "\\"
        for name in self.btn_names:
            if name == 'целиком':
                self.frames[name].add(path + 'mask.png', 10)
            else:
                self.frames[name].add(path + "columns\\" + name, 25)

class FullFoto:
    def __init__(self, parent, model, img_name, project_id, well_id):
        self.model = model
        self.well_id = well_id
        self.img_name = img_name
        im = Image.open(self.img_name)
        self.img = np.asarray(im)
        self.frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="#F5FFFA")

        self.k = self.img.shape[1] / self.img.shape[0]
        self.image = ctk.CTkImage(Image.open(self.img_name), size=(500, int(500 / self.k)))
        self.full_photo = ctk.CTkLabel(self.frame, text="", image=self.image)
        relwidth = 0.9
        relheight = relwidth / self.k
        self.full_photo.place(relwidth=0.9, relheight=relheight, relx=0.04, rely=0.02)

        self.table = ttk.Treeview(parent, show="headings")
        self.table['columns'] = self.model.heads

        for h in self.model.heads:
            self.table.heading(h, text=h, anchor='center')
            if h == "id":
                self.table.column(h, anchor='center', width=30, stretch=False)
            else:
                self.table.column(h, anchor='center', width=100, stretch=False)
        for i in self.model.heads:
            self.table.heading(i, text=i)

        self.well = self.model.projects[project_id]['wells'][well_id]

    def add(self, img_path, procent):
        image = ctk.CTkImage(Image.open(img_path), size=(500, int(500 / self.k)))
        image = ctk.CTkLabel(self.frame, text="", image=image)
        relwidth = 0.9
        relheight = relwidth / self.k
        image.place(relwidth=0.9, relheight=relheight, relx=0.04, rely=0.52)
        self.table.insert('', tk.END, values=(1, self.well_id, procent, '13-20', True, False))


class ColumnFrame:
    def __init__(self, parent, model, img_name, project_id, well_id):
        self.model = model
        self.well_id = well_id
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.img_name = self.file_path + "\\column\\clear\\" + img_name
        self.frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="#F5FFFA")

        self.c = ctk.CTkCanvas(self.frame, bg='white')
        self.c.place(relwidth=0.25, relheight=0.9, relx=0.08, rely=0.05)
        self.c.create_line(70, 0, 70, 650, width=2)
        self.c.create_polygon(70, 11, 65, 1, 75, 1)
        self.c.create_polygon(70, 638, 65, 649, 75, 649)

        for i in range(10):
            self.c.create_line(50, 11 + i * 80, 70, 11 + i * 80, width=1)
        for i in range(10):
            self.c.create_text(30, 11 + i * 80,
                               text="181." + str(i),
                               font="Verdana 8")

        image = Image.open(self.img_name)
        image = ctk.CTkImage(image, size=(60, 535))
        self.foto_column = ctk.CTkLabel(self.frame, text="", image=image)
        self.foto_column.place(relwidth=0.25, relheight=0.98, relx=0.35, rely=0.015)

        self.table = ttk.Treeview(parent, show="headings")
        self.table['columns'] = model.heads

        for h in model.heads:
            if h == "id":
                self.table.column(h, anchor='center', width=30, stretch=False)
            else:
                self.table.column(h, anchor='center', width=100, stretch=False)
        for i in model.heads:
            self.table.heading(i, text=i)

        self.btn_scaler = ctk.CTkButton(self.frame, text='', image=self.model.lupa, fg_color="white",
                                        command=lambda: self.scale_img(self.img_name))
        self.btn_scaler.place(relwidth=0.15, relheight=0.065, relx=0.45, rely=0.88)

        self.well = self.model.projects[project_id]['wells'][well_id]

    def add(self, img_path, procent):
        image = Image.open(img_path)
        image = ctk.CTkImage(image, size=(60, 535))

        image = ctk.CTkLabel(self.frame, text="", image=image)

        image.place(relwidth=0.25, relheight=0.98, relx=0.65, rely=0.015)
        self.table.insert('', tk.END, values=(1, self.well_id, procent, '13-20', True, False))
        self.btn_scaler1 = ctk.CTkButton(self.frame, text='', image=self.model.lupa, fg_color="white",
                                        command=lambda: self.scale_img(img_path))
        self.btn_scaler1.place(relwidth=0.15, relheight=0.065, relx=0.75, rely=0.88)


    def scale_img(self, img_path):
        photo = Image.open(img_path)
        b, g, r = photo.split()
        photo = Image.merge("RGB", (r, g, b))
        photo = ctk.CTkImage(photo, size=(75, 950))
        print(img_path)
        newW = ctk.CTk()
        newW.geometry('750x750')
        newW.title("Фото")
        newW.configure(bg='black')
        photo_label = ctk.CTkLabel(newW, bg_color="black", text='KEKEKEKKEKEKE', image=photo)
        photo_label.place(relwidth=0.25, relheight=1, relx=0.35, rely=0)
        newW.mainloop()




