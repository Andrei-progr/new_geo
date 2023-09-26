import os
import customtkinter as ctk
from tkinter import ttk
import easyocr
import numpy as np
import tkinter as tk
import threading
import pandas as pd
from PIL import Image, ImageOps, ImageTk
import cv2
from photo_editor import ImagePrediction
from tkinter import ttk


home_color = "#f5f2ff"
nav_color = "#c6c6ff"
import json
btn_color = "#6fe8a4"


def thread(func):
    def wrapper(*args, **kwargs):
        current_thread = threading.Thread(
            target=func, args=args, kwargs=kwargs)
        current_thread.start()
    return wrapper


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
        self.dir_path = os.path.dirname(os.path.realpath(self.img_name))

        ### Деление фото на колонки
        self.column_dir = os.listdir(self.dir_path + "\\columns")
        img = Image.open(self.img_name)
        b, g, r = img.split()
        self.img = Image.merge("RGB", (r, g, b)) #Синяя фотка
        self.imageMask = ImagePrediction(self.img)

        if len(self.column_dir) == 0:
            self.columns = self.imageMask.PredictColumns(self.dir_path)
            self.imageMask.DivideColumns(img, self.dir_path + "\\columns\\") #на вход - белая фотка
            self.column_dir = os.listdir(self.dir_path + "\\columns")
            begin, end = self.begin_end(self.img_name)
            self.model.counts_stat[self.img_name] = {}
            self.model.counts_stat[self.img_name]['begin'] = begin
            self.model.counts_stat[self.img_name]['end'] = end
            with open('counts.json', 'w') as outfile:
                json.dump(self.model.counts_stat, outfile)
        else:
            mask = Image.open(self.dir_path + "\\cols.png")
            mask = np.asarray(mask)
            self.imageMask.columns = mask
            self.columns = mask

        self.button_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#F5FFFA")
        self.button_frame.place(relwidth=0.1, relheight=0.5, relx=0.02, rely=0.1)
        self.lbl1 = ctk.CTkLabel(self.button_frame, text=["Choose", "Выберите \n изображение"][self.parent.lang], text_color="grey50")
        self.lbl1.place(relwidth=1, relheight=0.2, relx=0, rely=0)

        self.btn_names = [["full"], ['целиком']][self.parent.lang]
        for i in self.column_dir:
            self.btn_names.append(i)

        def create_pic_btn(name, counter):
            return ctk.CTkButton(self.button_frame, font=("Arial", 12),
                                 text=counter if counter != 0 else name, text_color="grey25", fg_color="#F5FFFA", hover_color="#6cdfff",
                                 image=self.model.z, anchor="w", command=lambda: self.review_column(name))

        self.btns = {}
        counter = 0
        for i in self.btn_names:
            self.btns[i] = create_pic_btn(i, counter)
            self.btns[i].place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.2 + 0.1 * counter)
            counter += 1

        s = ['full', 'целиком'][self.parent.lang]
        self.btns[s].configure(fg_color="#6cdfff", text_color="black")
        self.current_button = self.column_dir[0]

        self.frames = {}
        for i in self.btn_names:
            if i == ['full', 'целиком'][self.parent.lang]:
                f = FullFoto(self, self.model, self.img_name, project_id, well_id)
                self.frames[i] = f
            else:
                f = ColumnFrame(self, self.model, i, project_id, well_id, self.dir_path, self.img_name)
                self.frames[i] = f

        self.predict = ctk.CTkButton(self.frame, text=["Classify", "Классифицировать"][self.parent.lang], command = threading.Thread(target=self.to_predict).start)
        self.predict.configure(fg_color="#6fe8a4", text_color="black")
        self.predict.place(relwidth=0.14, relheight=0.06, relx=0.45, rely=0.9)

        self.save_pr = ctk.CTkButton(self.frame, text=["Save columns", "Сохранить колонки"][self.parent.lang], command = lambda: self.save_columns())
        self.save_pr.configure(fg_color="#6cdfff", text_color="black")
        self.save_pr.place(relwidth=0.14, relheight=0.06, relx=0.14, rely=0.9)

        self.csv = ctk.CTkButton(self.frame, text=["Save csv", "Сохранить csv"][self.parent.lang], command = lambda : self.save_table())
        self.csv.configure(fg_color="#6cdfff", text_color="black")
        self.csv.place(relwidth=0.14, relheight=0.06, relx=0.295, rely=0.9)

        self.btn1 = ctk.CTkButton(self.frame, text=["Destroyed", "Разрушенный"][self.parent.lang])
        self.btn1.configure(fg_color="grey75", text_color="black")
        self.btn1.place(relwidth=0.18, relheight=0.05, relx=0.6, rely=0.74)

        self.btn2 = ctk.CTkButton(self.frame, text=["Veins", "Прожилки"][self.parent.lang])
        self.btn2.configure(fg_color="grey75", text_color="black")
        self.btn2.place(relwidth=0.18, relheight=0.05, relx=0.6, rely=0.68)

        self.btn3 = ctk.CTkButton(self.frame, text=["Cracks", "Трещины"][self.parent.lang])
        self.btn3.configure(fg_color="grey75", text_color="black")
        self.btn3.place(relwidth=0.18, relheight=0.05, relx=0.79, rely=0.74)

        self.btn4 = ctk.CTkButton(self.frame, text=["Breed", "Порода"][self.parent.lang])
        self.btn4.configure(fg_color="grey75", text_color="black")
        self.btn4.place(relwidth=0.18, relheight=0.05, relx=0.79, rely=0.68)

        self.btn5 = ctk.CTkButton(self.frame, text=["Lithology", "Тектониты"][self.parent.lang])
        self.btn5.configure(fg_color="grey75", text_color="black")
        self.btn5.place(relwidth=0.37, relheight=0.05, relx=0.6, rely=0.62)

        self.back = ctk.CTkButton(self.frame, text=["Back", "Назад"][self.parent.lang], command=lambda: self.turn_back())
        self.back.configure(fg_color="#6cdfff", text_color="black")
        self.back.place(relwidth=0.1, relheight=0.06, relx=0.02, rely=0.02)

        self.beg_end_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#F5FFFA")
        self.beg_end_frame.place(relwidth=0.45, relheight=0.06, relx=0.14, rely=0.02)
        self.edit_dist = ctk.CTkLabel(self.beg_end_frame,
                                      text=["Edit \n length", "Редактировать \n длину"][self.parent.lang],
                                      text_color="grey50")
        self.edit_dist.place(relwidth=0.25, relheight=0.8, relx=0.05, rely=0.08)

        self.beg = ctk.CTkEntry(self.beg_end_frame, font=('Arial', 14))
        self.end = ctk.CTkEntry(self.beg_end_frame, font=('Arial', 14))
        self.beg.place(relwidth=0.2, relheight=0.6, relx=0.35, rely=0.2)
        self.end.place(relwidth=0.2, relheight=0.6, relx=0.58, rely=0.2)
        self.ok = ctk.CTkButton(self.beg_end_frame, fg_color="#6cdfff", text_color="black", text="ok", command=self.edit_length)
        self.ok.place(relwidth=0.15, relheight=0.6, relx=0.82, rely=0.2)

        self.brek = ctk.CTkLabel(self.frame, fg_color="#ba0b2b",
                                      text=["Brekchia", "Брекчия"][self.parent.lang],
                                      text_color="grey95")
        self.brek.place(relwidth=0.06, relheight=0.04, relx=0.04, rely=0.64)
        self.kat = ctk.CTkLabel(self.frame, fg_color="#fa73a4",
                                 text=["Kataklazit", "Катаклазит"][self.parent.lang],
                                 text_color="grey95")
        self.kat.place(relwidth=0.06, relheight=0.04, relx=0.04, rely=0.69)
        self.miel = ctk.CTkLabel(self.frame, fg_color="#eb637b",
                                 text=["Milonit", "Милонит"][self.parent.lang],
                                 text_color="grey95")
        self.miel.place(relwidth=0.06, relheight=0.04, relx=0.04, rely=0.74)
        self.brek.place_forget()
        self.kat.place_forget()
        self.miel.place_forget()

        destr_dir = os.listdir(self.dir_path + "\\destroyed")
        self.pred = False
        if len(destr_dir) != 0:
            self.pred = True

        if self.pred:
            self.change_type('destroyed')
            self.counts = self.model.counts_stat[self.img_name]['counts']
            self.btn1.configure(fg_color="#F5FFFA", command=lambda: self.change_type('destroyed'))
            self.btn2.configure(fg_color="#F5FFFA", command=lambda: self.change_type('prozhilki'))
            self.btn3.configure(fg_color="#F5FFFA", command=lambda: self.change_type('treshini'))
            self.btn4.configure(fg_color="#F5FFFA", command=lambda: self.change_type('poroda'))
            self.btn5.configure(fg_color="#F5FFFA", command=lambda: self.change_type('lito'))
            self.predict.configure(fg_color="grey75")

        self.review_column(['full', 'целиком'][self.parent.lang])


    def review_column(self, name):
        for j in self.btn_names:
            self.btns[j].configure(fg_color="#6cdfff" if j == name else "#F5FFFA")
        if self.current_button == name:
            pass
        else:
            self.frames[self.current_button].frame.place_forget()
            self.frames[self.current_button].table.place_forget()
            self.current_button = name
            if name == ['full', 'целиком'][self.parent.lang]:
                try:
                    self.frames[name].frame.place(relwidth=0.45, relheight=0.75, relx=0.14, rely=0.1)
                    self.frames[name].table.place(relwidth=0.37, relheight=0.5, relx=0.6, rely=0.1)
                except KeyError:
                    not_name = ['full', 'целиком'][not self.parent.lang]
                    self.frames[not_name].frame.place(relwidth=0.45, relheight=0.75, relx=0.14, rely=0.1)
                    self.frames[not_name].table.place(relwidth=0.37, relheight=0.5, relx=0.6, rely=0.1)
                self.beg_end_frame.place(relwidth=0.45, relheight=0.06, relx=0.14, rely=0.02)
            else:
                self.frames[name].frame.place(relwidth=0.32, relheight=0.75, relx=0.14, rely=0.1)
                self.frames[name].table.place(relwidth=0.47, relheight=0.5, relx=0.5, rely=0.1)
                self.beg_end_frame.place_forget()


    def to_predict(self):
        my_p = ttk.Progressbar(self.frame, orient='horizontal', length=200, mode='indeterminate')
        my_p.place(relwidth=0.37, relheight=0.05, relx=0.6, rely=0.8)
        my_p.start(10)
        methods = [self.imageMask.PredictDestroyed, self.imageMask.PredictProzhilki,
                   self.imageMask.PredictPoroda, self.imageMask.PredictCrack]
        paths = ['destroyed', 'prozhilki', 'poroda', 'treshini']
        colors = ([0,150,150], [85, 210, 0], [200, 150, 50], [250, 190, 250])
        for i in paths:
            self.model.clear(self.file_path + "\\masks\\" + i)
        for k in range(len(methods)):
            mask = methods[k]()
            img = cv2.resize(self.imageMask.img, (mask.shape[1], mask.shape[0]), #белый массив
                                        interpolation=cv2.INTER_AREA)
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    if mask[i, j] >= 125:
                        img[i, j] = colors[k]

            img = Image.fromarray(img) #синяя фотка
            b, g, r = img.split()
            img = Image.merge("RGB", (r, g, b)) #белая фотка
            mask = Image.fromarray(mask)
            mask = mask.convert("L")
            img.save(self.dir_path + "\\" + paths[k] + "\\mask.png")
            mask.save(self.file_path + "\\masks\\" + paths[k] + "\\" + "mask.png")
            self.imageMask.DivideColumns(img, self.dir_path + "\\" + paths[k] + "\\") #на вход - белая фотка
            self.imageMask.DivideColumns(mask, self.file_path + "\\masks\\" + paths[k] + "\\")

        self.predict_lito()

        self.count()

        my_p.place_forget()
        self.btn1.configure(fg_color="#F5FFFA", command=lambda: self.change_type('destroyed'))
        self.btn2.configure(fg_color="#F5FFFA", command=lambda: self.change_type('prozhilki'))
        self.btn3.configure(fg_color="#F5FFFA", command=lambda: self.change_type('treshini'))
        self.btn4.configure(fg_color="#F5FFFA", command=lambda: self.change_type('poroda'))
        self.btn5.configure(fg_color="#F5FFFA", command=lambda: self.change_type('lito'))
        self.predict.configure(fg_color = "grey75")

        kern = self.counts['poroda'][self.current_button]
        destr = self.counts['destroyed'][self.current_button]
        pr = self.counts['prozhilki'][self.current_button]
        tr = self.counts['treshini'][self.current_button]
        self.frames[self.current_button].table.insert(parent='', index='end', text='',
                                                      values=('full', self.well_id, 'e', tr, kern, destr, pr))
        self.change_type('destroyed')

    def predict_lito(self):
        colors = ([43, 11, 186], [164, 115, 250], [123, 99, 235])
        self.model.clear(self.file_path + "\\masks\\lito")
        mask = self.imageMask.PredictLithotypes()
        img = cv2.resize(self.imageMask.img, (mask.shape[1], mask.shape[0]),  # белый массив
                             interpolation=cv2.INTER_AREA)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if mask[i, j] == 80:
                    img[i, j] = colors[0]
                if mask[i, j] == 160:
                    img[i, j] = colors[1]
                if mask[i, j] == 240:
                    img[i,j] = colors[2]
        img = Image.fromarray(img)  # синяя фотка
        b, g, r = img.split()
        img = Image.merge("RGB", (r, g, b))  # белая фотка
        mask = Image.fromarray(np.uint8(mask[:,:,0]), 'L')
        img.save(self.dir_path + "\\lito\\mask.png")
        mask.save(self.file_path + "\\masks\\lito\\" + "mask.png")
        self.imageMask.DivideColumns(img, self.dir_path + "\\lito\\") #на вход - белая фотка
        self.imageMask.DivideColumns(mask, self.file_path + "\\masks\\lito\\")

    # Посчет статистики и процентов
    def count(self):
        self.counts = {}
        self.counts['destroyed'] = {}
        self.counts['poroda'] = {}
        self.counts['prozhilki'] = {}
        self.counts['treshini'] = {}
        self.counts['brek'] = {}
        self.counts['miel'] = {}
        self.counts['kat'] = {}
        all_kern = {}
        all_destr = {}
        begin = self.model.counts_stat[self.img_name]['begin']
        end = self.model.counts_stat[self.img_name]['end']
        length = end - begin
        crop_size = length / len(self.btn_names)

        for name in self.btn_names:
            if name == ['full', 'целиком'][self.parent.lang]:
                destr = Image.open(self.file_path + "\\masks\\destroyed\\mask.png")
                kern = Image.open(self.file_path + "\\masks\\poroda\\mask.png")
            else:
                destr = Image.open(self.file_path + "\\masks\\destroyed\\" + name)
                kern = Image.open(self.file_path + "\\masks\\poroda\\" + name)

            kern = np.asarray(kern)
            destr = np.asarray(destr)
            white1 = self.count_white(destr)
            white2 = self.count_white(kern)
            all_kern[name] = {}
            all_destr[name] = {}
            all_kern[name]['full'] = white2
            all_destr[name]['full'] = white1

            self.counts['destroyed'][name] = {}
            self.counts['poroda'][name] = {}
            self.counts['destroyed'][name]['full'] = (white1 / (white1 + white2)) * 100
            self.counts['poroda'][name]['full'] = (white2 / (white1 + white2)) * 100

            if name != ['full', 'целиком'][self.parent.lang]:
                crop_size = int(kern.shape[0] // 5)
                all_kern[name]['crops'] = []
                all_destr[name]['crops'] = []
                self.counts['destroyed'][name]['crops'] = []
                self.counts['poroda'][name]['crops'] = []

                for i in range(5):
                    cr_white1 = self.count_white(kern[i * crop_size: (i + 1) * crop_size, :])
                    cr_white2 = self.count_white(destr[i * crop_size: (i + 1) * crop_size, :])
                    all_kern[name]['crops'].append(cr_white1)
                    all_destr[name]['crops'].append(cr_white2)
                    try:
                        self.counts['poroda'][name]['crops'].append((cr_white1 / (cr_white1 + cr_white2)) * 100)
                        self.counts['destroyed'][name]['crops'].append((cr_white2 / (cr_white1 + cr_white2)) * 100)
                    except ZeroDivisionError:
                        self.counts['poroda'][name]['crops'].append(np.nan)
                        self.counts['destroyed'][name]['crops'].append(np.nan)

        for name in self.btn_names:
            if name == ['full', 'целиком'][self.parent.lang]:
                pr = Image.open(self.file_path + "\\masks\\prozhilki\\mask.png")
                tr = Image.open(self.file_path + "\\masks\\treshini\\mask.png")
                lito = Image.open(self.file_path + "\\masks\\lito\\mask.png")
            else:
                pr = Image.open(self.file_path + "\\masks\\prozhilki\\" + name)
                tr = Image.open(self.file_path + "\\masks\\treshini\\" + name)
                lito = Image.open(self.file_path + "\\masks\\lito\\" + name)

            pr = np.asarray(pr)
            tr = np.asarray(tr)
            lito = np.asarray(lito)
            white1 = self.count_white(pr)
            white2 = self.count_white(tr, treshini=True)
            white_brek, white_miel, white_kat = self.count_white(lito, kern_type=True)

            self.counts['prozhilki'][name] = {}
            self.counts['treshini'][name] = {}
            self.counts['brek'][name] = {}
            self.counts['miel'][name] = {}
            self.counts['kat'][name] = {}

            all = all_kern[name]['full'] + all_destr[name]['full']
            self.counts['prozhilki'][name]['full'] = (white1 / all) * 100
            self.counts['treshini'][name]['full'] = white2
            self.counts['brek'][name]['full'] = (white_brek / all) * 100
            self.counts['miel'][name]['full'] = (white_miel / all) * 100
            self.counts['kat'][name]['full'] = (white_kat / all) * 100

            if name != ['full', 'целиком'][self.parent.lang]:
                crop_size = int(pr.shape[0] // 5)
                self.counts['prozhilki'][name]['crops'] = []
                self.counts['treshini'][name]['crops'] = []
                self.counts['brek'][name]['crops'] = []
                self.counts['miel'][name]['crops'] = []
                self.counts['kat'][name]['crops'] = []

                for i in range(5):
                    cr_white1 = self.count_white(pr[i * crop_size: (i + 1) * crop_size, :])
                    cr_white2 = self.count_white(tr[i * crop_size: (i + 1) * crop_size, :], treshini=True)
                    cr_white_brek, cr_white_miel, cr_white_kat = self.count_white(lito[i * crop_size : (i + 1) * crop_size], kern_type=True)
                    cr_all = all_kern[name]['crops'][i] + all_destr[name]['crops'][i]
                    try:
                        self.counts['prozhilki'][name]['crops'].append(
                            (cr_white1 / cr_all) * 100)
                        self.counts['brek'][name]['crops'].append(
                            (cr_white_brek / cr_all) * 100)
                        self.counts['miel'][name]['crops'].append(
                            (cr_white_miel / cr_all) * 100)
                        self.counts['kat'][name]['crops'].append(
                            (cr_white_kat / cr_all) * 100)
                    except ZeroDivisionError:
                        self.counts['prozhilki'][name]['crops'].append(np.nan)
                        self.counts['brek'][name]['crops'].append(np.nan)
                        self.counts['miel'][name]['crops'].append(np.nan)
                        self.counts['kat'][name]['crops'].append(np.nan)
                    self.counts['treshini'][name]['crops'].append(cr_white2)

        self.model.counts_stat[self.img_name]['counts'] = self.counts
        with open('counts.json', 'w') as outfile:
             json.dump(self.model.counts_stat, outfile)

    #Подсчет пикселей класса и количества трещин для одной маски
    def count_white(self, mask, treshini = False, kern_type = False):

        if not kern_type:
            ret, thr_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
            if not treshini:
                try:
                    white = np.unique(thr_mask, return_counts=True)[1][1]
                except IndexError:
                    white = 0
            else:
                try:
                    contours, hirerchy = cv2.findContours(thr_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
                    white = len(hirerchy[0])
                except:
                    white = 0
            return white
        else:
            nums = np.unique(mask, return_counts=True)
            try:
                idx = list(nums[0]).index(80)
                brek = nums[1][idx]
            except ValueError:
                brek = 0
            try:
                idx = list(nums[0]).index(160)
                kat = nums[1][idx]
            except ValueError:
                kat = 0
            try:
                idx = list(nums[0]).index(240)
                miel = nums[1][idx]
            except ValueError:
                miel = 0

            return brek, miel, kat


    def change_type(self, type):
        self.btn1.configure(fg_color = "#6cdfff" if type == 'destroyed' else "#F5FFFA")
        self.btn2.configure(fg_color = "#6cdfff" if type == 'prozhilki' else "#F5FFFA")
        self.btn3.configure(fg_color = "#6cdfff" if type == 'treshini' else "#F5FFFA")
        self.btn4.configure(fg_color = "#6cdfff" if type == 'poroda' else "#F5FFFA")
        self.btn5.configure(fg_color = "#6cdfff" if type == 'lito' else "#F5FFFA")
        path = self.dir_path + "\\" + type + "\\"
        for name in self.btn_names:
            if name == ['full', 'целиком'][self.parent.lang]:
                self.frames[name].add(path + 'mask.png', name)
            else:
                self.frames[name].add(path + "\\" + name, name)
        if type == 'lito':
            self.brek.place(relwidth=0.06, relheight=0.04, relx=0.04, rely=0.64)
            self.kat.place(relwidth=0.06, relheight=0.04, relx=0.04, rely=0.69)
            self.miel.place(relwidth=0.06, relheight=0.04, relx=0.04, rely=0.74)
        else:
            self.brek.place_forget()
            self.kat.place_forget()
            self.miel.place_forget()

    def save_columns(self):
        os.mkdir(self.dir_path + "\\full")
        h = self.imageMask.img.shape[0]
        w = self.imageMask.img.shape[1]
        mask = cv2.resize(self.columns, (w, h), cv2.INTER_LINEAR)
        self.imageMask.columns = mask
        img = self.img
        b, g, r = img.split()
        img = Image.merge("RGB", (r, g, b))
        a = self.imageMask.DivideColumns(img, self.dir_path + "\\full\\", h)
        self.imageMask.columns = self.columns

    def begin_end(self, img_path):
        reader = easyocr.Reader(['ru'])
        p = Image.open(img_path)
        p = np.asarray(p)
        result = reader.readtext(p,
                                 paragraph=True, y_ths=0.1, x_ths=0.1)
        print(result)
        begin = 0
        end = 5
        idx = 0
        for i in range(len(result)):
            res = result[i][1]
            if res.find('Инт') != -1 or res.find('инт') != -1:
                st = res
                pos = st.find(" ")
                number = st[pos + 1:]
                number = number.replace(',', '.')
                try:
                    begin = float(number)
                    idx = i
                    break
                except ValueError:
                    number = result[i + 1][1]
                    number = number.replace('|', '')
                    number = number.replace('[', '')
                    number = number.replace(']', '')
                    number = number.replace(',', '.')
                    try:
                        begin = float(number)
                    except ValueError:
                        begin = 0
                    idx = i + 1
                    break

        st_end = result[idx + 1][1]
        pos = st_end.find(" ")
        if pos != -1:
            end_number = st_end[:pos]
        else:
            end_number = st_end
        end_number = end_number.replace(',', '.')
        try:
            end = float(end_number)
        except ValueError:
            end = begin + 5

        if begin > end:
            if begin - end > 90:
                begin = begin - 100
            else:
                end = begin + 5
        return begin, end

    def turn_back(self):
        from projects_and_wells import Well
        p = Well(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page = p.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def save_table(self):
        try:
            os.mkdir(self.dir_path + "\\csv")
        except FileExistsError:
            pass
        for id, page in self.frames.items():
            df = pd.DataFrame(columns = self.model.heads)
            for c in page.table.get_children():
                val = page.table.item(c)['values']
                df.loc[len(df.index)] = val
            pos = id.find('.')
            if pos != -1:
                id = id[:pos]
            df.to_csv(self.dir_path + "\\csv\\" + id + ".csv")

    def edit_length(self):
        new_b = self.beg.get()
        new_e = self.end.get()
        if new_b != '':
            begin = float(self.beg.get())
            self.model.counts_stat[self.img_name]['begin'] = begin
        if new_e != '':
            end = float(self.end.get())
            self.model.counts_stat[self.img_name]['end'] = end
        for id, f in self.frames.items():
            if id != 'целиком':
                try:
                    f.change_length()
                except AttributeError:
                    continue
        with open('counts.json', 'w') as outfile:
            json.dump(self.model.counts_stat, outfile)


class FullFoto:
    def __init__(self, parent, model, img_name, project_id, well_id):
        self.model = model
        self.parent = parent
        self.well_id = well_id
        self.img_name = img_name
        self.name = self.img_name.replace(parent.dir_path, '')
        im = Image.open(self.img_name)
        self.img = np.asarray(im)
        self.frame = ctk.CTkFrame(parent.frame, corner_radius=10, fg_color="#F5FFFA")

        self.k = self.img.shape[1] / self.img.shape[0]
        self.image = ctk.CTkImage(Image.open(self.img_name), size=(500, int(500 / self.k)))
        self.full_photo = ctk.CTkLabel(self.frame, text="", image=self.image)
        relwidth = 0.9
        relheight = relwidth / self.k
        self.full_photo.place(relwidth=0.9, relheight=relheight, relx=0.04, rely=0.02)

        self.table = ttk.Treeview(parent.frame, show="headings")
        self.table['columns'] = self.model.heads
        style = ttk.Style()
        style.theme_use('clam')
        treeScrollx = ttk.Scrollbar(self.table, orient='horizontal')
        treeScrollx.configure(command=self.table.xview)
        self.table.configure(xscrollcommand=treeScrollx.set)
        treeScrollx.pack(side="bottom", fill='both')

        self.table.bind("<Double-1>", self.click_motion)

        for h in self.model.heads:
            self.table.heading(h, text=h, anchor='center')
            if h == "id":
                self.table.column(h, anchor='center', width=30, stretch=False)
            else:
                self.table.column(h, anchor='center', width=90, stretch=False)
        for i in self.model.heads:
            self.table.heading(i, text=i)

        self.btn_scaler = ctk.CTkButton(self.frame, text='', image=self.model.lupa, fg_color="white",
                                        command=lambda: self.scale_img(self.img_name))
        self.btn_scaler.place(relwidth=0.12, relheight=0.065, relx=0.82, rely=0.37)
        self.well = self.model.projects[project_id]['wells'][well_id]

    def add(self, img_path, name):
        image = ctk.CTkImage(Image.open(img_path), size=(500, int(500 / self.k)))
        image = ctk.CTkLabel(self.frame, text="", image=image)
        relwidth = 0.9
        relheight = relwidth / self.k
        image.place(relwidth=0.9, relheight=relheight, relx=0.04, rely=0.52)

        for i in self.table.get_children():
            self.table.delete(i)
        try:
            kern = float(self.model.counts_stat[self.img_name]['counts']['poroda'][name]['full'])
        except KeyError:
            if name == 'целиком':
                name = 'full'
            else:
                name = 'целиком'
            kern = float(self.model.counts_stat[self.img_name]['counts']['poroda'][name]['full'])
        destr = float(self.model.counts_stat[self.img_name]['counts']['destroyed'][name]['full'])
        pr = float(self.model.counts_stat[self.img_name]['counts']['prozhilki'][name]['full'])
        tr = self.model.counts_stat[self.img_name]['counts']['treshini'][name]['full']
        brek = float(self.model.counts_stat[self.img_name]['counts']['brek'][name]['full'])
        miel = float(self.model.counts_stat[self.img_name]['counts']['miel'][name]['full'])
        kat = float(self.model.counts_stat[self.img_name]['counts']['kat'][name]['full'])

        kern = float('{:.1f}'.format(kern))
        destr = float('{:.1f}'.format(destr))
        pr = float('{:.1f}'.format(pr))
        brek = float('{:.1f}'.format(brek))
        miel = float('{:.1f}'.format(miel))
        kat = float('{:.1f}'.format(kat))

        self.table.insert(parent='', index='end', text='', iid = str(-1),
                                                      values=('1', self.well_id, self.name, tr, kern, destr, pr, brek, kat, miel))
        self.btn_scaler = ctk.CTkButton(self.frame, text='', image=self.model.lupa, fg_color="white",
                                        command=lambda: self.scale_img(img_path))
        self.btn_scaler.place(relwidth=0.12, relheight=0.065, relx=0.82, rely=0.85)

    def click_motion(self, event):
        region = self.table.identify_region(event.x, event.y)
        if region != 'cell':
            return
        iid = self.table.focus()
        col = self.table.identify_column(event.x)
        print(col)
        st = self.table.identify_row(event.y)
        print("строка ", st)
        row_id = int(st)
        print(row_id)
        column_id = int(col[1:]) - 1
        value = self.table.item(iid)['values'][column_id]
        bbox = self.table.bbox(iid, col)
        entry_edit = tk.Entry(self.table, width=bbox[2])

        entry_edit.editing_column_index = column_id
        entry_edit.editing_item_iid = iid

        def on_enter_pressed(event):
            types = {3 : 'treshini', 4 : 'poroda', 5 : 'destroyed', 6 : 'prozhilki', 7 : 'brek', 8 : 'kat', 9 : 'miel'}
            new_text = event.widget.get()
            current_values = self.table.item(iid).get('values')
            if column_id == 3:
                new_text = int(new_text)
                current_values[column_id] = new_text
            else:
                try:
                    new_text = float(new_text)
                    current_values[column_id] = float('{:.1f}'.format(new_text))
                except:
                    event.widget.destroy()
                    return
            if column_id == 4:
                s = 100 - float(new_text)
                current_values[column_id + 1] = s
                if s < 0 or s > 100:
                    event.widget.destroy()
                    return
                try:
                    self.model.counts_stat[self.img_name]['counts']['destroyed']['целиком']['full'] = float(s)
                except KeyError:
                    self.model.counts_stat[self.img_name]['counts']['destroyed']['full']['full'] = float(s)
            if column_id == 5:
                s = 100 - float(new_text)
                current_values[column_id - 1] = s
                if s < 0 or s > 100:
                    event.widget.destroy()
                    return
                try:
                    self.model.counts_stat[self.img_name]['counts']['poroda']['целиком']['full'] = float(s)
                except KeyError:
                    self.model.counts_stat[self.img_name]['counts']['poroda']['full']['full'] = float(s)
            self.table.item(iid, values = current_values)
            try:
                self.model.counts_stat[self.img_name]['counts'][types[column_id]]['целиком']['full'] = new_text
            except KeyError:
                self.model.counts_stat[self.img_name]['counts'][types[column_id]]['full']['full'] = new_text

            with open('counts.json', 'w') as outfile:
                json.dump(self.model.counts_stat, outfile)
            event.widget.destroy()

        entry_edit.insert(0, value)
        entry_edit.select_range(0, tk.END)
        entry_edit.focus()
        entry_edit.bind("<FocusOut>", self.on_focus_out)
        entry_edit.bind("<Return>", on_enter_pressed)
        entry_edit.place(x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])


    def on_focus_out(self, event):
        event.widget.destroy()

    def scale_img(self, image_path):
        newWindow = ctk.CTkToplevel(self.parent.parent)
        newWindow.geometry("700x700")
        newWindow.wm_attributes("-topmost", 1)
        newWindow.title(["Increase", "Увеличение"][self.parent.parent.lang])
        newWindow.config(bg="black")
        photo = Image.open(image_path)
        photo = ctk.CTkImage(photo, size=(1350, 600))
        photo_label = ctk.CTkLabel(newWindow, bg_color="black", text='', image=photo)
        photo_label.place(relwidth=1, relheight=0.9, relx=0, rely=0.1)
        newWindow.mainloop()


class ColumnFrame:
    def __init__(self, parent, model, img_name, project_id, well_id, path, full_img_name):
        self.model = model
        self.well_id = well_id
        self.parent = parent
        self.col_name = img_name
        self.img_name = path + "\\columns\\" + img_name
        self.frame = ctk.CTkFrame(parent.frame, corner_radius=10, fg_color="#F5FFFA")
        self.full_img_name = full_img_name
        self.name = self.full_img_name.replace(parent.dir_path, '')
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        number = int(self.col_name[:1]) - 1
        l = len(self.parent.btn_names) - 1
        self.dist = (self.model.counts_stat[self.full_img_name]['end'] - self.model.counts_stat[self.full_img_name]['begin']) / l
        self.begin = self.model.counts_stat[self.full_img_name]['begin'] + number * self.dist
        self.end = self.begin + self.dist

        self.c = ctk.CTkCanvas(self.frame, bg='white')
        self.c.place(relwidth=0.25, relheight=0.9, relx=0.08, rely=0.05)

        def canvas_motion(event):
            canvas_height = event.height
            print("Высота канваса ", canvas_height)
            canvas_width = event.width
            self.draw_canvas(canvas_width, canvas_height)

        self.c.bind("<Configure>", canvas_motion)

        image = Image.open(self.img_name)
        w_koef = 75 / 1920
        h_koef = 670 / 1080
        w_pic = int(w_koef * self.parent.parent.width)
        h_pic = int(h_koef * self.parent.parent.heigth)
        print("Высота картинки ", h_pic)
        image = ctk.CTkImage(image)
        #image = tk.PhotoImage(self.img_name)
        self.foto_column = ctk.CTkLabel(self.frame, text="", image=image)
        self.foto_column.place(relwidth=0.25, relheight=0.98, relx=0.35, rely=0.01)

        self.table = ttk.Treeview(parent.frame, show="headings")
        self.table['columns'] = model.heads

        def table_motion(event):
            w = event.width
            for h in model.heads:
                if h == "id":
                    self.table.column(h, anchor='center', width = int(w * 0.08), stretch=False)
                else:
                    self.table.column(h, anchor='center', width = int(w * 0.08), stretch=False)
            for i in model.heads:
                self.table.heading(i, text=i)

        style = ttk.Style()
        style.theme_use('clam')
        treeScrollx = ttk.Scrollbar(self.table, orient='horizontal')
        treeScrollx.configure(command=self.table.xview)
        self.table.configure(xscrollcommand=treeScrollx.set)
        treeScrollx.pack(side="bottom", fill='both')

        self.table.bind("<Double-1>", self.click_motion)
        self.parent.frame.bind("<Configure>", table_motion)
        self.btn_scaler = ctk.CTkButton(self.frame, text='', image=self.model.lupa, fg_color="white",
                                        command=lambda: self.scale_img(self.img_name))
        self.btn_scaler.place(relwidth=0.12, relheight=0.065, relx=0.52, rely=0.88)
        self.well = self.model.projects[project_id]['wells'][well_id]


    def draw_canvas(self, canvas_width, canvas_height):
        self.c.delete('all')
        p = self.dist / 5
        self.c.create_line(canvas_width * 0.5, 0,
                           canvas_width * 0.5, canvas_height, width=2)
        crop_size = int((canvas_height * 0.976) // 5)
        for i in range(5):
            self.c.create_line(canvas_width * 0.3501, canvas_height * 0.015 + i * crop_size,
                               canvas_width * 0.65, canvas_height * 0.015 + i * crop_size, width=1)
        for i in range(5):
            n = self.begin + i * p
            n = float('{:.3f}'.format(n))
            self.c.create_text(canvas_width * 0.2, canvas_height * 0.015 + i * crop_size,
                               text=str(n),
                               font="Verdana 8")
        self.c.create_line(canvas_width * 0.35, canvas_height * 0.987,
                           canvas_width * 0.65, canvas_height * 0.987, width=1)
        self.c.create_text(canvas_width * 0.2, canvas_height * 0.984,
                           text=str(float('{:.3f}'.format(self.end))),
                           font="Verdana 8")


    def click_motion(self, event):
        region = self.table.identify_region(event.x, event.y)
        if region != 'cell':
            return
        iid = self.table.focus()
        col = self.table.identify_column(event.x)
        print(col)
        st = self.table.identify_row(event.y)
        print("строка ", st)
        row_id = int(st)
        print(row_id)
        column_id = int(col[1:]) - 1
        value = self.table.item(iid)['values'][column_id]
        bbox = self.table.bbox(iid, col)
        entry_edit = tk.Entry(self.table, width=bbox[2])

        entry_edit.editing_column_index = column_id
        entry_edit.editing_item_iid = iid

        def on_enter_pressed(event):
            types = {3 : 'treshini', 4 : 'poroda', 5 : 'destroyed', 6 : 'prozhilki', 7 : 'brek', 8 : 'kat', 9 : 'miel'}
            new_text = event.widget.get()
            current_values = self.table.item(iid).get('values')
            if column_id == 3:
                new_text = int(new_text)
                current_values[column_id] = new_text
            else:
                try:
                    new_text = float(new_text)
                    current_values[column_id] = float('{:.1f}'.format(new_text))
                except:
                    event.widget.destroy()
                    return

            if column_id == 4:
                s = 100 - float(new_text)
                current_values[column_id + 1] = s
                if s < 0 or s > 100:
                    event.widget.destroy()
                    return
                if row_id > 0:
                    self.model.counts_stat[self.full_img_name]['counts']['destroyed'][self.col_name]['crops'][row_id] = float(s)
                else:
                    self.model.counts_stat[self.full_img_name]['counts']['destroyed'][self.col_name]['full'] = float(s)
            if column_id == 5:
                s = 100 - float(new_text)
                current_values[column_id - 1] = s
                if s < 0 or s > 100:
                    event.widget.destroy()
                    return
                if row_id > -1:
                    self.model.counts_stat[self.full_img_name]['counts']['poroda'][self.col_name]['crops'][row_id] = float(s)
                else:
                    self.model.counts_stat[self.full_img_name]['counts']['poroda'][self.col_name]['full'] = float(s)
            self.table.item(iid, values = current_values)
            if row_id == -1:
                self.model.counts_stat[self.full_img_name]['counts'][types[column_id]][self.col_name]['full'] = new_text
            else:
                self.model.counts_stat[self.full_img_name]['counts'][types[column_id]][self.col_name]['crops'][row_id] = new_text
                print()
            with open('counts.json', 'w') as outfile:
                json.dump(self.model.counts_stat, outfile)
            event.widget.destroy()

        entry_edit.insert(0, value)
        entry_edit.select_range(0, tk.END)
        entry_edit.focus()
        entry_edit.bind("<FocusOut>", self.on_focus_out)
        entry_edit.bind("<Return>", on_enter_pressed)
        entry_edit.place(x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])

    def on_focus_out(self, event):
        event.widget.destroy()

    def entry_size(self, event):
        event.widget.destroy()

    def add(self, img_path, name):
        image = Image.open(img_path)
        w_koef = 60 / 1920
        h_koef = 535 / 1080
        w_pic = int(w_koef * self.parent.parent.width)
        h_pic = int(h_koef * self.parent.parent.heigth)
        image = ctk.CTkImage(image, size=(w_pic, h_pic))
        image = ctk.CTkLabel(self.frame, text="", image=image)
        image.place(relwidth=0.25, relheight=1, relx=0.65, rely=0)

        self.btn_scaler1 = ctk.CTkButton(self.frame, text='', image=self.model.lupa, fg_color="white",
                                        command=lambda: self.scale_img(img_path))
        self.btn_scaler1.place(relwidth=0.12, relheight=0.065, relx=0.82, rely=0.88)

        for i in self.table.get_children():
            self.table.delete(i)

        self.counts = self.model.counts_stat[self.full_img_name]['counts']

        try:
            full_kern = float(self.counts['poroda'][name]['full'])
        except KeyError:
            if name == 'целиком':
                name = 'full'
            else:
                name = 'full'
            full_kern = float(self.counts['poroda'][name]['full'])

        full_destr = float(self.counts['destroyed'][name]['full'])
        full_pr = float(self.counts['prozhilki'][name]['full'])
        full_tr = self.counts['treshini'][name]['full']
        full_br = float(self.counts['brek'][name]['full'])
        full_miel = float(self.counts['miel'][name]['full'])
        full_kat = float(self.counts['kat'][name]['full'])

        full_kern = float('{:.1f}'.format(full_kern))
        full_destr = float('{:.1f}'.format(full_destr))
        full_pr = float('{:.1f}'.format(full_pr))
        full_br = float('{:.1f}'.format(full_br))
        full_miel = float('{:.1f}'.format(full_miel))
        full_kat = float('{:.1f}'.format(full_kat))

        self.table.insert(parent='', index='end', text='', iid = str(-1),
                                                      values=('full', self.well_id, self.name, full_tr, full_kern, full_destr, full_pr, full_br, full_kat, full_miel))
        length = len(self.counts['poroda'][name]['crops'])
        pp = self.dist / length
        for i in range(length):
            k = float(self.counts['poroda'][name]['crops'][i])
            d = float(self.counts['destroyed'][name]['crops'][i])
            p = float(self.counts['prozhilki'][name]['crops'][i])
            if p > 100:
                p = 100.0
            t = self.counts['treshini'][name]['crops'][i]
            brek = float(self.counts['brek'][name]['crops'][i])
            miel = float(self.counts['miel'][name]['crops'][i])
            kat = float(self.counts['kat'][name]['crops'][i])

            k = float('{:.1f}'.format(k))
            d = float('{:.1f}'.format(d))
            p = float('{:.1f}'.format(p))
            brek = float('{:.1f}'.format(brek))
            miel = float('{:.1f}'.format(miel))
            kat = float('{:.1f}'.format(kat))

            start_n = self.begin + i * pp
            stop_n = start_n + pp
            start_n = float('{:.3f}'.format(start_n))
            stop_n = float('{:.3f}'.format(stop_n))
            inter = str(start_n) + "-" + str(stop_n)
            self.table.insert(parent='', index='end', text='', iid = str(i),
                              values=(inter, self.well_id, self.name, t, k, d, p, brek, kat, miel))

    def change_length(self):
        number = int(self.col_name[:1]) - 1
        l = len(self.parent.btn_names) - 1
        self.dist = (self.model.counts_stat[self.full_img_name]['end'] - self.model.counts_stat[self.full_img_name][
            'begin']) / l
        self.begin = self.model.counts_stat[self.full_img_name]['begin'] + number * self.dist
        self.end = self.begin + self.dist
        g = GeoColumn(self.parent.parent, self.model, self.parent.project_id, self.well_id, self.full_img_name)
        self.model.current_page = g.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


    def scale_img(self, image_path):
        newWindow = ctk.CTkToplevel(self.parent.parent)
        newWindow.geometry("700x700")
        newWindow.wm_attributes("-topmost", 1)
        newWindow.title(["Increase", "Увеличение"][self.parent.parent.lang])
        newWindow.config(bg="black")
        photo = Image.open(image_path)
        photo = ctk.CTkImage(photo, size=(65, 950))
        photo_label = ctk.CTkLabel(newWindow, bg_color="black", text='', image=photo)
        photo_label.place(relwidth=0.25, relheight=0.98, relx=0.35, rely=0.01)
        newWindow.mainloop()





