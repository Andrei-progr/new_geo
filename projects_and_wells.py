import shutil

import customtkinter as ctk
import cv2
import tkinter.filedialog as fd
from PIL import Image, UnidentifiedImageError
import os
from tkinter import ttk
home_color = "#f5f2ff"
nav_color = "#c6c6ff"
scroll_color = "#87CEFA"
import json
from page_geo_column import GeoColumn
import tkinter as tk
import pandas as pd
import threading

def thread(func):
    def wrapper(*args, **kwargs):
        current_thread = threading.Thread(
            target=func, args=args, kwargs=kwargs)
        current_thread.start()
    return wrapper

class NewProject:
    def __init__(self, parent, model):
        self.model = model
        self.parent = parent
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color = home_color)
        self.text1 = ctk.CTkLabel(self.frame, font = ("Comic Sans MS", 20, "bold"), text = ["New project", "Новый проект"][self.parent.lang])
        self.text1.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.02)
        self.text2 = ctk.CTkLabel(self.frame, text=["Project name", "Название проекта"][self.parent.lang])
        self.text2.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.1)
        self.entry1 = ctk.CTkEntry(self.frame, width=350)
        self.entry1.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.2)
        self.text3 = ctk.CTkLabel(self.frame, text=["Date", "Дата начала проекта"][self.parent.lang])
        self.text3.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.3)
        self.entry2 = ctk.CTkEntry(self.frame, width=350)
        self.entry2.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.4)
        self.text4 = ctk.CTkLabel(self.frame, text=["User", "Имя пользователя"][self.parent.lang])
        self.text4.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.5)
        self.entry3 = ctk.CTkEntry(self.frame, width=350)
        self.entry3.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.6)

        self.back = ctk.CTkButton(self.frame, text = ["Back", "Назад"][self.parent.lang], corner_radius=10,
                                  fg_color="#6cdfff", text_color="black",
                                  command = self.return_home)
        self.back.place(relwidth=0.15, relheight=0.08, relx=0.05, rely=0.05)

        self.create = ctk.CTkButton(self.frame, text=["Create", "Создать"][self.parent.lang], corner_radius=10,
                                    fg_color="#6cdfff", text_color = "black",
                                    command = self.create_project)
        self.create.place(relwidth=0.45, relheight=0.08, relx=0.2, rely=0.9)

    def return_home(self):
        from main_page import HomePage
        self.model.current_page.grid_forget()
        f = HomePage(self.parent, self.model)
        self.model.current_page = f.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def create_project(self):
        pr_name = self.entry1.get()
        print(pr_name)
        if pr_name == '':
            pr_name = 'Без названия' + "(" + str(len(self.model.projects)) + ")"
        date = self.entry2.get()
        user_name = self.entry3.get()
        self.model.projects[pr_name] = {'date' : date, 'user_name' : user_name, 'wells' : {}}
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)

        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + pr_name)
        new_well = Project(self.parent, self.model, pr_name)
        self.model.current_page.grid_forget()
        self.model.current_page = new_well.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


class Project:
    def __init__(self, parent, model, pr_name):
        self.model = model
        self.parent = parent
        self.project_id = pr_name
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color = home_color)
        self.parent.title(self.project_id)
        self.filename = 'not'
        self.dirname = 'not'

        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.head_frame = ctk.CTkFrame(self.frame, corner_radius=30, fg_color="#F5FFFA")
        self.head_frame.place(relwidth=0.77, relheight=0.1, relx=0.12, rely=0.05)
        self.wells_buttons = []
        wells = self.model.projects[self.project_id]['wells']
        def create_buttons(command):
            return ctk.CTkButton(self.frame, font=("Arial", 14),
                                                        text=command, text_color="grey25", fg_color="#6cdfff",
                                                        command=lambda: self.open_well(command))
        if len(wells) != 0:
            for key in wells:
                 self.wells_buttons.append(create_buttons(key))

        for i in range(len(self.wells_buttons)):
            self.wells_buttons[i].place(relwidth=0.3, relheight=0.08, relx=0.5, rely = 0.2 + i * 0.1)

        self.new_well = ctk.CTkButton(self.frame, text=["Add well", "Добавить скважину"][self.parent.lang], font=("Arial", 14),
                                      corner_radius=10, fg_color="#6cdfff", text_color="black",
                                      image=self.model.plus, compound="left", command = self.add_well)
        self.new_well.place(relwidth=0.3, relheight=0.1, relx=0.1, rely=0.2)


    def add_well(self):
        self.new_well_frame = ctk.CTkFrame(self.frame, corner_radius=20, fg_color="#F5FFFA")
        self.text8 = ctk.CTkLabel(self.new_well_frame, text=["Well name", "Название скважины"][self.parent.lang], font=("Arial", 14))
        self.text8.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.02)
        self.entry6 = ctk.CTkEntry(self.new_well_frame)
        self.entry6.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.11)
        self.text9 = ctk.CTkLabel(self.new_well_frame, text=["Deep", "Глубина"][self.parent.lang],
                                  font=("Arial", 14))
        self.text9.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.22)
        self.entry7 = ctk.CTkEntry(self.new_well_frame)
        self.entry7.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.31)
        self.load = ctk.CTkButton(self.new_well_frame, text=["Load box", "Загрузить ящик"][self.parent.lang], font=("Arial", 14),
                                      corner_radius=10, fg_color="#6cdfff", text_color="grey25",
                                      image=self.model.plus, compound="left", command = self.load_photo)
        self.load.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.46)

        self.load_dir = ctk.CTkButton(self.new_well_frame, text=["Load directory", "Загрузить папку"][self.parent.lang], font=("Arial", 14),
                                      corner_radius=10, fg_color="#6cdfff", text_color="grey25",
                                      image=self.model.plus, compound="left", command = self.load_dir)
        self.load_dir.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.6)

        self.close = ctk.CTkButton(self.new_well_frame, text=["Cancel", "Отмена"][self.parent.lang], font=("Arial", 14),
                                        corner_radius=10, fg_color="#ff926e", text_color="grey25", command = self.close_frame)
        self.close.place(relwidth=0.35, relheight=0.12, relx=0.55, rely=0.83)
        self.save = ctk.CTkButton(self.new_well_frame, text=["Open", "Открыть"][self.parent.lang], font=("Arial", 14),
                                        corner_radius=10, fg_color="#6cdfff", text_color="grey25", command = self.open)
        self.save.place(relwidth=0.35, relheight=0.12, relx=0.1, rely=0.83)
        self.new_well_frame.place(relwidth=0.3, relheight=0.65, relx=0.1, rely=0.35)


    def close_frame(self):
        self.new_well_frame.place_forget()
        pass

    def load_photo(self):
        self.filename = fd.askopenfilename(initialdir = self.file_path)
        self.loaded = ctk.CTkLabel(self.new_well_frame, text=["Loaded sucsessfully", "Ящик загружен"][self.parent.lang], font=('Arial', 14))
        self.loaded.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.7)

    def load_dir(self):
        self.dirname = fd.askdirectory()
        self.loaded = ctk.CTkLabel(self.new_well_frame, text=["Load sucsessfully", "Загружено успешно"][self.parent.lang], font=('Arial', 14))
        self.loaded.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.7)

    def get_name(self, filepath):
        filepath = filepath[::-1]
        p = filepath.find('/')
        filepath = filepath[:p]
        return filepath[::-1]

    def open(self):
        name = self.entry6.get()
        deep = self.entry7.get()
        if name == '':
            message = ['Please, enter a name', 'Пожалуйста, введите название'][self.parent.lang]
            self.warnings(message)
            return
        if deep == '':
            message = ['Please, enter a deep', 'Пожалуйста, введите глубину'][self.parent.lang]
            self.warnings(message)
            return
        path = os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + self.project_id + "\\" + name
        os.mkdir(path)
        a = {'deep': deep, 'photos': []}
        self.model.projects[self.project_id]['wells'][name] = a

        if self.filename != 'not':
            photo_name = self.get_name(self.filename)
            self.create_photo(path, photo_name, name)
        if self.dirname != 'not':
            photo_list = os.listdir(self.dirname)
            for i in photo_list:
                self.create_photo(path, i, name)
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)

        well = Well(self.parent, self.model, self.project_id, name)
        self.model.current_page.grid_forget()
        self.model.current_page = well.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


    def create_photo(self, path, photo_name, well_name):
        os.mkdir(path + "\\" + photo_name)
        if self.filename != 'not':
            img = Image.open(self.filename)
        if self.dirname != 'not':
            try:
                img = Image.open(self.dirname + "\\" + photo_name)
            except UnidentifiedImageError:
                return
        img.save(path + "\\" + photo_name + "\\" + photo_name)
        os.mkdir(path + "\\" + photo_name + "\\" + "columns")
        os.mkdir(path + "\\" + photo_name + "\\" + "destroyed")
        os.mkdir(path + "\\" + photo_name + "\\" + "prozhilki")
        os.mkdir(path + "\\" + photo_name + "\\" + "treshini")
        os.mkdir(path + "\\" + photo_name + "\\" + "poroda")
        os.mkdir(path + "\\" + photo_name + "\\" + "lito")
        try:
            self.model.projects[self.project_id]['wells'][well_name]['photos'].append(photo_name)
        except AttributeError:
            pass

    def open_well(self, well_id):
        well = Well(self.parent, self.model, self.project_id, well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = well.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def warnings(self, message):
        newWindow = ctk.CTkToplevel(self.parent)
        newWindow.geometry("350x350")
        newWindow.wm_attributes("-topmost", 1)
        newWindow.title(["Warning", "Ошибка"][self.parent.lang])
        warn_label = ctk.CTkLabel(newWindow, bg_color="grey95", text = message, font = ('Arial', 18))
        warn_label.place(relwidth=0.9, relheight=0.35, relx=0.06, rely=0.1)
        newWindow.mainloop()


class Well:
    def __init__(self, parent, model, project_id, well_id):
        self.model = model
        self.parent = parent
        self.project_id = project_id
        self.well_id = well_id
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color = home_color)
        self.photo_list = self.model.projects[self.project_id]['wells'][well_id]['photos']
        self.file_path = os.path.dirname(os.path.realpath(__file__))

        self.scrollbar = ctk.CTkScrollableFrame(self.frame, corner_radius=10, fg_color = "#69BBAC")
        self.scrollbar.place(relwidth=0.55, relheight=0.88, relx=0.15, rely=0.05)
        self.scrollbar.grid_rowconfigure(len(self.photo_list), weight=1)
        self.scrollbar.grid_columnconfigure(0, weight=1)

        def create_open_button(box, command):
            return ctk.CTkButton(box, text=["Open", "Открыть"][self.parent.lang], font=("Arial", 12),
                                     corner_radius=10, fg_color="#6cdfff", text_color="black", command = lambda : self.open_geo(command))
        def create_delete_button(box, command):
            return ctk.CTkButton(box, text=["Delete", "Удалить"][self.parent.lang], font=("Arial", 12), command = lambda : self.delete(command),
                          corner_radius=10, fg_color="#ff926e", text_color="black")

        def create_descriptions(box, path_name, img_name):
            label = ctk.CTkLabel(box, text=img_name, fg_color="#F5FFFA", text_color = "grey25", font=("Arial", 14))
            try:
                is_pred = self.model.counts_stat[path_name]['counts']
                is_pred = True
            except KeyError:
                is_pred = False
            if is_pred:
                pred = ctk.CTkLabel(box, text = ['Predicted', 'Предсказано'][self.parent.lang],
                                    fg_color="#4fe84d", corner_radius=14, text_color="grey95")
            else:
                pred = ctk.CTkLabel(box, text = ['Not predicted', 'Не предсказано'][self.parent.lang],
                                    fg_color="#fc3d49", corner_radius=14, text_color="grey95")
            return label, pred

        self.btns_open = []
        self.btns_delete = []
        self.boxes = []
        self.pics = []
        self.labels = []
        self.predictions = {}
        for i in range(len(self.photo_list)):
            name = self.file_path + "\\projects\\" + str(self.project_id) + "\\" + str(self.well_id) + "\\" + self.photo_list[i] + "\\" + self.photo_list[i]
            im = ctk.CTkImage(Image.open(name), size=(250, 100))
            self.boxes.append(ctk.CTkFrame(self.scrollbar, corner_radius=10, fg_color="#F5FFFA"))
            box = self.boxes[i]
            self.btns_open.append(create_open_button(box, name))
            self.btns_delete.append(create_delete_button(box, self.photo_list[i]))
            self.pics.append(ctk.CTkLabel(box, text="", image = im))
            l, p = create_descriptions(box, name, self.photo_list[i])
            self.labels.append(l)
            self.predictions[self.photo_list[i]] = p

        for i in range(len(self.photo_list)):
            # self.boxes[i].place(relwidth=0.45, relheight=0.22, relx=0.2, rely=0.05 + i * 0.25)
            self.boxes[i].grid(row=i, padx=50, pady=20, sticky='ew')
            self.pics[i].place(relwidth=0.65, relheight=0.65, relx=0, rely=0.25)
            self.btns_open[i].place(relwidth=0.3, relheight=0.2, relx=0.65, rely=0.32)
            self.btns_delete[i].place(relwidth=0.3, relheight=0.2, relx=0.65, rely=0.62)
            self.labels[i].place(relwidth=0.45, relheight=0.1, relx=0.1, rely=0.1)
            self.predictions[self.photo_list[i]].place(relwidth=0.3, relheight=0.12, relx=0.65, rely=0.1)

        self.deep = self.model.projects[self.project_id]['wells'][self.well_id]['deep']
        self.button_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#F5FFFA")
        self.button_frame.place(relwidth=0.25, relheight=0.65, relx=0.72, rely=0.05)
        self.well_name = ctk.CTkLabel(self.button_frame, text=self.well_id + " - " + str(self.deep), fg_color="#69BBAC",
                                      text_color="grey99", corner_radius=10, font = ('Arial', 16))
        self.well_name.place(relwidth=0.75, relheight=0.08, relx=0.15, rely=0.03)
        self.edit_deep = ctk.CTkLabel(self.button_frame, text=['Edit deep', 'Редактировать глубину'][self.parent.lang],
                                      fg_color="#F5FFFA", text_color="grey50", corner_radius=10, font = ('Arial', 14))
        self.edit_deep.place(relwidth=0.75, relheight=0.06, relx=0.15, rely=0.14)
        self.deep_entry = ctk.CTkEntry(self.button_frame, font=('Arial', 14), text_color="grey25")
        self.deep_entry.place(relwidth=0.58, relheight=0.07, relx=0.15, rely=0.21)
        self.ok = ctk.CTkButton(self.button_frame, fg_color="#6cdfff", text_color="black", text="ok", command=self.to_edit)
        self.ok.place(relwidth=0.15, relheight=0.07, relx=0.76, rely=0.21)

        self.add = ctk.CTkButton(self.button_frame, text=["Add box", "Добавить ящик"][self.parent.lang], font=("Arial", 14),
                                 corner_radius=10, fg_color="#6cdfff", image=self.model.plus, compound="left",
                                 text_color="grey25", command = self.load_photo)
        self.add.place(relwidth=0.75, relheight=0.08, relx=0.15, rely=0.32)

        self.column = ctk.CTkButton(self.button_frame, text=["Column", "Колонка"][self.parent.lang],
                                     font=("Arial", 14),
                                     corner_radius=10, fg_color="#6cdfff", text_color="grey25", command=self.geo_column)
        self.column.place(relwidth=0.75, relheight=0.08, relx=0.15, rely=0.42)

        self.save = ctk.CTkButton(self.button_frame, text=["Save", "Сохранить скважину"][self.parent.lang],
                                    font=("Arial", 14),
                                    corner_radius=10, fg_color="#6cdfff", text_color="grey25", command=self.save_all_csv)
        self.save.place(relwidth=0.75, relheight=0.08, relx=0.15, rely=0.52)

        self.predict = ctk.CTkButton(self.button_frame, text=["Predict all", "Классифицировать все"][self.parent.lang],
                                     font=("Arial", 14),
                                     corner_radius=10, fg_color="#6fe8a4", text_color="grey25",
                                     command=self.predict_all)
        self.predict.place(relwidth=0.75, relheight=0.08, relx=0.15, rely=0.85)

        self.back = ctk.CTkButton(self.frame, text=["Back", "Назад"][self.parent.lang], font=("Arial", 14),
                                        corner_radius=10, fg_color="#6cdfff", text_color="black", command = self.turn_back)
        self.back.place(relwidth=0.09, relheight=0.08, relx=0.03, rely=0.05)

    def to_edit(self):
        new_deep = self.deep_entry.get()
        if new_deep == '':
            return
        try:
            new_deep = float(new_deep)
        except ValueError:
            message = ["Enter a number", "Введите числовое значение"][self.parent.lang]
            self.warnings(message)
            return
        self.model.projects[self.project_id]['wells'][self.well_id]['deep'] = new_deep
        self.deep = new_deep
        self.deep_entry.delete(0, tk.END)
        self.well_name.configure(text = self.well_id + " - " + str(self.deep))
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)

    def get_name(self, filepath):
        filepath = filepath[::-1]
        p = filepath.find('/')
        filepath = filepath[:p]
        return filepath[::-1]

    def load_photo(self):
        self.filename = fd.askopenfilename(initialdir = self.file_path)
        if self.filename == "":
            return
        photo_name = self.get_name(self.filename)
        self.model.projects[self.project_id]['wells'][self.well_id]['photos'].append(photo_name)
        path = os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + self.project_id + "\\" + self.well_id

        os.mkdir(path + "\\" + photo_name)
        img = Image.open(self.filename)
        img.save(path + "\\" + photo_name + "\\" + photo_name)
        os.mkdir(path + "\\" + photo_name + "\\" + "columns")
        os.mkdir(path + "\\" + photo_name + "\\" + "destroyed")
        os.mkdir(path + "\\" + photo_name + "\\" + "prozhilki")
        os.mkdir(path + "\\" + photo_name + "\\" + "treshini")
        os.mkdir(path + "\\" + photo_name + "\\" + "poroda")
        os.mkdir(path + "\\" + photo_name + "\\" + "lito")

        w = Well(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = w.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)

    def delete(self, name):
        self.model.projects[self.project_id]['wells'][self.well_id]['photos'].remove(name)
        self.photo_list = self.model.projects[self.project_id]['wells'][self.well_id]['photos']
        w = Well(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = w.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)
        path = self.file_path + "\\projects\\" + str(self.project_id) + "\\" + str(self.well_id) + "\\" + name
        shutil.rmtree(path)

    @thread
    def predict_all(self):
        my_p = ttk.Progressbar(self.frame, orient='horizontal', length=200, mode='indeterminate')
        my_p.place(relwidth=0.25, relheight=0.06, relx=0.72, rely=0.86)
        my_p.start(20)
        label = ctk.CTkLabel(self.frame, fg_color="#F5FFFA", text=['Processing ', 'Обработка '][self.parent.lang])
        label.place(relwidth=0.25, relheight=0.1, relx=0.72, rely=0.74)
        self.predict.configure(fg_color="#3b6ca9")
        for i in range(len(self.photo_list)):
            img_name = self.file_path + "\\projects\\" + str(self.project_id) + "\\" + str(self.well_id) + "\\" + self.photo_list[i] + "\\" + self.photo_list[i]
            g = GeoColumn(self.parent, self.model, self.project_id, self.well_id, img_name)
            label.configure(text=['Processing ', 'Обрабатывается '][self.parent.lang] + "\n" + self.photo_list[i])
            if g.pred:
                continue
            g.to_predict()
            self.predictions[self.photo_list[i]].configure(fg_color="#4fe84d", text='Предсказано')
        my_p.place_forget()
        label.place_forget()
        w = Well(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = w.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def save_all_csv(self):
        for i in range(len(self.photo_list)):
            img_name = self.file_path + "\\projects\\" + str(self.project_id) + "\\" + str(self.well_id) + "\\" + self.photo_list[i] + "\\" + self.photo_list[i]
            g = GeoColumn(self.parent, self.model, self.project_id, self.well_id, img_name)
            g.save_table()

    def turn_back(self):
        p = Project(self.parent, self.model, self.project_id)
        self.model.current_page.grid_forget()
        self.model.current_page = p.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def open_geo(self, img_name):
        g = GeoColumn(self.parent, self.model, self.project_id, self.well_id, img_name)
        self.model.current_page.grid_forget()
        self.model.current_page = g.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def geo_column(self):
        c = Column(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = c.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def warnings(self, message):
        newWindow = ctk.CTkToplevel(self.parent)
        newWindow.geometry("350x350")
        newWindow.wm_attributes("-topmost", 1)
        newWindow.title(["Warning", "Ошибка"][self.parent.lang])
        warn_label = ctk.CTkLabel(newWindow, bg_color="grey95", text = message, font = ('Arial', 18))
        warn_label.place(relwidth=0.9, relheight=0.35, relx=0.06, rely=0.1)
        newWindow.mainloop()


class Column:
    def __init__(self, parent, model, project_id, well_id):
        self.model = model
        self.parent = parent
        self.project_id = project_id
        self.well_id = well_id
        self.photo_list = self.model.projects[self.project_id]['wells'][self.well_id]['photos']
        self.deep = float(self.model.projects[self.project_id]['wells'][self.well_id]['deep'])
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + "\\" + "projects" + "\\" + self.project_id + "\\" + self.well_id

        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color=home_color)
        self.back = ctk.CTkButton(self.frame, text=["Back", "Назад"][self.parent.lang],
                                  command=lambda: self.turn_back())
        self.back.configure(fg_color="#6cdfff", text_color="black")
        self.back.place(relwidth=0.1, relheight=0.06, relx=0.02, rely=0.02)

        #self.table = ctk.CTkScrollableFrame(self.frame, corner_radius=10, fg_color = "#69BBAC")
        self.table_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color = "#69BBAC")
        self.table_frame.place(relwidth=0.85, relheight=0.8, relx=0.1, rely=0.1)
        header = ['interval', 'data', 'box', 'edit', 'cracks', 'kern', 'destroyed', 'veins', 'brekchia', 'cataclazit', 'milonit', 'description']

        style = ttk.Style()
        style.theme_use('clam')
        # Add a Treeview widget and set the selection mode
        self.tree = ttk.Treeview(self.table_frame, show='headings', height=10, selectmode="browse")
        self.tree['columns'] = header

        self.save_column = ctk.CTkButton(self.table_frame, text=["Save", "Сохранить"][self.parent.lang], fg_color="#6cdfff",
                                         command=lambda: self.to_save_column(), text_color = "grey25")
        self.save_column.place(relwidth=0.2, relheight=0.06, relx=0.08, rely=0.92)

        for h in header:
            self.tree.heading(h, text=h, anchor='center')
            if h == "id":
                self.tree.column(h, anchor='center', width=100, stretch=False)
            else:
                self.tree.column(h, anchor='center', width=110, stretch=False)
        for i in header:
            self.tree.heading(i, text=i)

        # Adding a vertical scrollbar to Treeview widget
        treeScrolly = ttk.Scrollbar(self.tree)
        treeScrolly.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeScrolly.set)
        treeScrolly.pack(side="right", fill="both")

        treeScrollx = ttk.Scrollbar(self.tree, orient='horizontal')
        treeScrollx.configure(command=self.tree.xview)
        self.tree.configure(xscrollcommand=treeScrollx.set)
        treeScrollx.pack(side="bottom", fill='both')
        self.tree.place(relwidth=0.8, relheight=0.3, relx=0.02, rely=0.02)

        self.begins = {}
        self.ends = {}
        path = self.file_path
        for i in self.photo_list:
            img_path = path + "\\" + i + "\\" + i
            try:
                beg = self.model.counts_stat[img_path]['begin']
                self.begins[i] = beg
                end = self.model.counts_stat[img_path]['end']
                self.ends[i] = end
            except KeyError:
                continue

        self.begins = dict(sorted(self.begins.items(), key=lambda item: item[1]))
        self.ends = dict(sorted(self.ends.items(), key=lambda item: item[1]))
        self.header = header
        print(self.begins)
        print(self.ends)

        name = 'целиком'
        last_end = 0
        counter = 0
        self.intersection = False
        self.over_deep = False
        for i, value in self.begins.items():
            if value < last_end:
                self.intersection = True
            if abs(value - last_end) > 0.2 and value > last_end:
                inter = str(last_end) + "-" + str(value)
                self.tree.insert(parent='', index='end', text='', iid = str(counter),
                                 values=(inter, 'NO', '--', '--', '--', '--', '--', '--', '--', '--', '--', 'add..'))
                counter += 1
            img_name = self.file_path + "\\" + i + "\\" + i
            des = os.listdir(self.file_path + "\\" + i + "\\destroyed")

            if len(des) == 0:
                inter = str(value) + "-" + str(self.ends[i])
                self.tree.insert(parent='', index='end', text='', iid=str(counter),
                                 values=(inter, "YES", i, 'OPEN', "--", "--", "--", "--", '--', '--', '--', 'add..'))
                counter += 1
                last_end = self.ends[i]
                continue

            try:
                kern = float(self.model.counts_stat[img_name]['counts']['poroda'][name]['full'])
            except KeyError:
                name = 'full'
                kern = float(self.model.counts_stat[img_name]['counts']['poroda'][name]['full'])

            destr = float(self.model.counts_stat[img_name]['counts']['destroyed'][name]['full'])
            pr = float(self.model.counts_stat[img_name]['counts']['prozhilki'][name]['full'])
            tr = self.model.counts_stat[img_name]['counts']['treshini'][name]['full']
            br = float(self.model.counts_stat[img_name]['counts']['brek'][name]['full'])
            miel = float(self.model.counts_stat[img_name]['counts']['miel'][name]['full'])
            kat = float(self.model.counts_stat[img_name]['counts']['kat'][name]['full'])

            kern = float('{:.1f}'.format(kern))
            destr = float('{:.1f}'.format(destr))
            pr = float('{:.1f}'.format(pr))
            br = float('{:.1f}'.format(br))
            miel = float('{:.1f}'.format(miel))
            kat = float('{:.1f}'.format(kat))

            inter = str(value) + "-" + str(self.ends[i])
            self.tree.insert(parent='', index='end', text='', iid=str(counter),
                             values=(inter, "YES", i, 'OPEN', tr, kern, destr, pr, br, kat, miel, 'add..'))
            counter += 1
            last_end = self.ends[i]

        if abs(last_end - self.deep) > 0.1 and last_end < self.deep:
            inter = str(last_end) + "-" + str(self.deep)
            self.tree.insert(parent='', index='end', text='', iid=str(counter),
                             values=(inter, "NO", "--", '--', "--", "--", "--", "--", "--", "--", "--", 'add..'))
        if last_end > self.deep:
            self.over_deep = True

        if self.intersection:
            self.label1 = ctk.CTkLabel(self.table_frame, text = ['Intersection', 'Пересечение отрезков'][self.parent.lang],
                                    fg_color="#fc3d49", corner_radius=14, text_color="grey95")
            self.label1.place(relwidth=0.18, relheight=0.05, relx=0.08, rely=0.03)
        if self.over_deep:
            self.label2 = ctk.CTkLabel(self.table_frame,
                                       text=['Out-of-well', 'Выход за указанное значение глубины'][self.parent.lang],
                                       fg_color="#fc3d49", corner_radius=14, text_color="grey95")
            self.label2.place(relwidth=0.25, relheight=0.05, relx=0.28, rely=0.03)
        self.tree.place(relwidth=0.8, relheight=0.8, relx=0.08, rely=0.1)
        self.tree.bind("<Double-1>", self.click_motion)

    def turn_back(self):
        p = Well(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page = p.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def to_save_column(self):
        df = pd.DataFrame(columns = self.header)
        for c in self.tree.get_children():
            val = self.tree.item(c)['values']
            df.loc[len(df.index)] = val
        df.to_csv(self.file_path + "\\" + self.well_id + ".csv")

    def click_motion(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        iid = self.tree.focus()
        col = self.tree.identify_column(event.x)
        st = self.tree.identify_row(event.y)
        print("строка ", st)
        row_id = int(st)
        column_id = int(col[1:]) - 1
        print("col", column_id)
        value = self.tree.item(iid)['values'][column_id]
        name = self.tree.item(iid)['values'][2]
        if value == 'OPEN':
            img_name = self.file_path + "\\" + name + "\\" + name
            g = GeoColumn(self.parent, self.model, self.project_id, self.well_id, img_name)
            self.model.current_page.grid_forget()
            self.model.current_page = g.frame
            self.model.current_page.grid(row=0, column=1, sticky="nsew")
            return

        bbox = self.tree.bbox(iid, col)
        entry_edit = tk.Entry(self.tree, width=bbox[2])

        entry_edit.editing_column_index = column_id
        entry_edit.editing_item_iid = iid

        def on_enter_pressed(event):
            new_text = event.widget.get()
            current_values = self.tree.item(iid).get('values')
            current_values[column_id] = new_text
            self.tree.item(iid, values=current_values)
            event.widget.destroy()

        entry_edit.insert(0, value)
        entry_edit.select_range(0, tk.END)
        entry_edit.focus()
        entry_edit.bind("<FocusOut>", self.on_focus_out)
        entry_edit.bind("<Return>", on_enter_pressed)
        entry_edit.place(x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])


    def on_focus_out(self, event):
        event.widget.destroy()
