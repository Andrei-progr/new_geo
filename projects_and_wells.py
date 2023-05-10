import customtkinter as ctk
import cv2
import tkinter.filedialog as fd
from PIL import Image
import os
from tkinter import ttk
home_color = "#f5f2ff"
nav_color = "#c6c6ff"
import json
from page_geo_column import GeoColumn
from photo_editor import ImagePrediction


class NewProject:
    def __init__(self, parent, model):
        self.model = model
        self.parent = parent
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color = home_color)
        self.text1 = ctk.CTkLabel(self.frame, font = ("Comic Sans MS", 20, "bold"), text = "Новый проект")
        self.text1.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.02)
        self.text2 = ctk.CTkLabel(self.frame, text="Название проекта")
        self.text2.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.1)
        self.entry1 = ctk.CTkEntry(self.frame, width=350)
        self.entry1.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.2)
        self.text3 = ctk.CTkLabel(self.frame, text="Дата начала проекта")
        self.text3.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.3)
        self.entry2 = ctk.CTkEntry(self.frame, width=350)
        self.entry2.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.4)
        self.text4 = ctk.CTkLabel(self.frame, text="Имя пользователя")
        self.text4.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.5)
        self.entry3 = ctk.CTkEntry(self.frame, width=350)
        self.entry3.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.6)

        self.back = ctk.CTkButton(self.frame, text = "Назад", command = self.return_home)
        self.back.place(relwidth=0.15, relheight=0.08, relx=0.05, rely=0.05)

        self.create = ctk.CTkButton(self.frame, text="Создать", command = self.create_project)
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

        self.new_well = ctk.CTkButton(self.frame, text="Добавить скважину", font=("Arial", 14),
                                      corner_radius=10, fg_color="#6cdfff", text_color="black",
                                      image=self.model.plus, compound="left", command = self.add_well)
        self.new_well.place(relwidth=0.3, relheight=0.1, relx=0.1, rely=0.2)


    def add_well(self):
        self.new_well_frame = ctk.CTkFrame(self.frame, corner_radius=20, fg_color="#F5FFFA")
        self.text8 = ctk.CTkLabel(self.new_well_frame, text="Название скважины")
        self.text8.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.05)
        self.entry6 = ctk.CTkEntry(self.new_well_frame)
        self.entry6.place(relwidth=0.8, relheight=0.15, relx=0.1, rely=0.25)
        self.load = ctk.CTkButton(self.new_well_frame, text="Загрузить ящик", font=("Arial", 12),
                                      corner_radius=10, fg_color="#6cdfff", text_color="black",
                                      image=self.model.plus, compound="left", command = self.load_photo)
        self.load.place(relwidth=0.8, relheight=0.18, relx=0.1, rely=0.5)

        self.close = ctk.CTkButton(self.new_well_frame, text="Отмена", font=("Arial", 12),
                                        corner_radius=10, fg_color="#ff926e", text_color="black", command = self.close_frame)
        self.close.place(relwidth=0.35, relheight=0.12, relx=0.55, rely=0.8)
        self.save = ctk.CTkButton(self.new_well_frame, text="Открыть", font=("Arial", 12),
                                        corner_radius=10, fg_color="#6cdfff", text_color="black", command = self.open)
        self.save.place(relwidth=0.35, relheight=0.12, relx=0.1, rely=0.8)
        self.new_well_frame.place(relwidth=0.3, relheight=0.5, relx=0.1, rely=0.4)


    def close_frame(self):
        self.new_well_frame.place_forget()
        pass

    def load_photo(self):
        self.filename = fd.askopenfilename(initialdir = self.file_path)
        img = cv2.imread(self.filename)
        self.loaded = ctk.CTkLabel(self.new_well_frame, text="Ящик загружен")
        self.loaded.place(relwidth=0.8, relheight=0.12, relx=0.1, rely=0.68)

    def open(self):
        name = self.entry6.get()
        a = {'deep' : 180, 'photos' : []}
        self.model.projects[self.project_id]['wells'][name] = a
        try:
            self.model.projects[self.project_id]['wells'][name]['photos'].append(self.filename)
        except AttributeError:
            pass
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)

        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + self.project_id + "\\" + name)
        well = Well(self.parent, self.model, self.project_id, name)
        self.model.current_page.grid_forget()
        self.model.current_page = well.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


    def open_well(self, well_id):
        well = Well(self.parent, self.model, self.project_id, well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = well.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")



class Well:
    def __init__(self, parent, model, project_id, well_id):
        self.model = model
        self.parent = parent
        self.project_id = project_id
        self.well_id = well_id
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color = home_color)
        self.photo_list = self.model.projects[self.project_id]['wells'][well_id]['photos']
        self.file_path = os.path.dirname(os.path.realpath(__file__))

        def create_open_button(box, command):
            return ctk.CTkButton(box, text="Открыть", font=("Arial", 12),
                                     corner_radius=10, fg_color="#6cdfff", text_color="black", command = lambda : self.open_geo(command))
        def create_delete_button(box, command):
            return ctk.CTkButton(box, text="Удалить", font=("Arial", 12),
                          corner_radius=10, fg_color="#ff926e", text_color="black")

        self.btns_open = []
        self.btns_delete = []
        self.boxes = []
        self.pics = []
        for i in range(len(self.photo_list)):
            name = self.photo_list[i]
            im = ctk.CTkImage(Image.open(name), size=(200, 100))
            self.boxes.append(ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#F5FFFA"))
            box = self.boxes[i]
            self.btns_open.append(create_open_button(box, name))
            self.btns_delete.append(create_delete_button(box, name))
            self.pics.append(ctk.CTkLabel(box, text="", image = im))

        for i in range(len(self.photo_list)):
            self.boxes[i].place(relwidth=0.45, relheight=0.22, relx=0.2, rely=0.05 + i * 0.25)
            self.pics[i].place(relwidth=0.55, relheight=0.65, relx=0, rely=0.15)
            self.btns_open[i].place(relwidth=0.35, relheight=0.2, relx=0.6, rely=0.2)
            self.btns_delete[i].place(relwidth=0.35, relheight=0.2, relx=0.6, rely=0.55)

        self.add = ctk.CTkButton(self.frame, text="Добавить ящик", font=("Arial", 14),
                                        corner_radius=10, fg_color="#6cdfff", text_color="black", command = self.load_photo)
        self.add.place(relwidth=0.35, relheight=0.12, relx=0.2, rely=0.8)

        self.back = ctk.CTkButton(self.frame, text="Назад", font=("Arial", 14),
                                        corner_radius=10, fg_color="#6cdfff", text_color="black", command = self.turn_back)
        self.back.place(relwidth=0.09, relheight=0.08, relx=0.05, rely=0.05)


    def load_photo(self):
        self.filename = fd.askopenfilename(initialdir = self.file_path + "\\kern\\data")
        self.model.projects[self.project_id]['wells'][self.well_id]['photos'].append(self.filename)
        s = self.filename
        s = s[::-1]
        pos = s.find('/')
        s = s[:pos]
        s = s[::-1]
        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + self.project_id + "\\" + self.well_id + "\\" + s)
        w = Well(self.parent, self.model, self.project_id, self.well_id)
        self.model.current_page.grid_forget()
        self.model.current_page = w.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)

    def turn_back(self):
        p = Project(self.parent, self.model, self.project_id)
        self.model.current_page = p.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")

    def open_geo(self, img_name):
        g = GeoColumn(self.parent, self.model, self.project_id, self.well_id, img_name)
        self.model.current_page = g.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")







