import shutil
import pandas as pd
import customtkinter as ctk
from tkinter import ttk
from projects_and_wells import NewProject, Project
home_color = "#f5f2ff"
# home_color = "#FFFFE0"
nav_color = "#c6c6ff"
import json
import tkinter.filedialog as fd
import os
import numpy as np
import tkinter as tk

class HomePage:
    def __init__(self, parent, model):
        self.model = model
        self.parent = parent
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color=home_color)
        self.new_project = ctk.CTkButton(self.frame, text=["New project", "Новый проект"][self.parent.lang], image=model.plus, compound="left",
                                         command=self.new_project)
        self.new_project.configure(fg_color="#6cdfff", text_color="black", corner_radius=20, width=175, height=50)
        self.new_project.place(relwidth=0.5, relheight=0.1, relx=0.2, rely=0.1)

        self.load_pr = ctk.CTkButton(self.frame, text=["Load project", "Загрузить проект"][self.parent.lang], image=model.plus,
                                     compound="left", command = self.load_project)
        self.load_pr.configure(fg_color="#6cdfff", text_color="black", corner_radius=20, width=150, height=50)
        self.load_pr.place(relwidth=0.5, relheight=0.1, relx=0.2, rely=0.25)

    def get_name(self, filepath):
        filepath = filepath[::-1]
        p = filepath.find('/')
        filepath = filepath[:p]
        return filepath[::-1]

    def load_project(self):
        import datetime
        self.dirname = fd.askdirectory()
        if self.dirname == "":
            return
        project_id = self.get_name(self.dirname)
        date = str(datetime.datetime.now())
        self.model.projects[project_id] = {'date' : date, 'user_name' : "User", 'wells' : {}}

        types_list = ['columns', 'destroyed', 'lito', 'poroda', 'prozhilki', 'treshini', 'csv', 'cols.png']
        predict_types = ['destroyed', 'lito', 'poroda', 'prozhilki', 'treshini']
        well_list = os.listdir(self.dirname)
        if len(well_list) == 0:
            message = ['Empty project', 'Пустой проект'][self.parent.lang]
            self.warnings(message)
            return
        for well in well_list:
            box_list = os.listdir(self.dirname + "\\" + well)
            for box in box_list:
                box_dirs = os.listdir(self.dirname + "\\" + well + "\\" + box)
                for name in types_list:
                    try:
                        idx = box_dirs.index(name)
                    except ValueError:
                        message = [f'Missing {name} in drawer: ', f'Не хватает {name} в ящике: '][self.parent.lang] + box
                        self.warnings(message)
                        return
                counter = 0
                for i in range(len(predict_types)):
                    files = os.listdir(self.dirname + "\\" + well + "\\" + box + "\\" + predict_types[i])
                    l = len(files)
                    if i == 0:
                        counter = l
                    else:
                        if l != counter:
                            message = ['Different number of files in dirs', 'Разное количество файлов в папках'][
                                          self.parent.lang]
                            self.warnings(message)
                            return

        shutil.copytree(self.dirname, os.path.dirname(os.path.realpath(__file__)) + "\\projects\\" + project_id)
        for well in well_list:
            self.model.projects[project_id]['wells'][well] = {'deep': 180, 'photos': []}
            box_list = os.listdir(self.dirname + "\\" + well)
            for box in box_list:
                self.model.projects[project_id]['wells'][well]['photos'].append(box)
                files = os.listdir(self.dirname + "\\" + well + "\\" + box)
                if files.index('csv') == -1:
                    return
                counts = {}
                counts['destroyed'] = {}
                counts['poroda'] = {}
                counts['prozhilki'] = {}
                counts['treshini'] = {}
                counts['brek'] = {}
                counts['miel'] = {}
                counts['kat'] = {}
                csv = os.listdir(self.dirname + "\\" + well + "\\" + box + "\\csv\\")
                length = len(csv)
                begin = 0
                end = 100
                for df_name in csv:
                    df = pd.read_csv(self.dirname + "\\" + well + "\\" + box + "\\csv\\" + df_name)
                    if len(df) == 1:
                        pos = df_name.find(".")
                        df_name = df_name[:pos]
                    else:
                        pos = df_name.find(".")
                        df_name = df_name[:pos] + ".png"
                    counts['destroyed'][df_name] = {}
                    counts['poroda'][df_name] = {}
                    counts['prozhilki'][df_name] = {}
                    counts['treshini'][df_name] = {}
                    counts['brek'][df_name] = {}
                    counts['miel'][df_name] = {}
                    counts['kat'][df_name] = {}

                    counts['destroyed'][df_name]['full'] = float(df.destroyed.values[0])
                    counts['poroda'][df_name]['full'] = float(df.kern.values[0])
                    counts['prozhilki'][df_name]['full'] = float(df.veins.values[0])
                    counts['treshini'][df_name]['full'] = int(df.cracks.values[0])
                    counts['brek'][df_name]['full'] = float(df.breckchia.values[0])
                    counts['miel'][df_name]['full'] = float(df.milonit.values[0])
                    counts['kat'][df_name]['full'] = float(df.cataclasit.values[0])
                    if len(df) == 1:
                        continue
                    else:
                        counts['destroyed'][df_name]['crops'] = list(df.destroyed.values[1:])
                        counts['poroda'][df_name]['crops'] = list(df.kern.values[1:])
                        counts['prozhilki'][df_name]['crops'] = list(df.veins.values[1:])
                        counts['treshini'][df_name]['crops'] = []
                        for c in df.cracks.values[1:]:
                            counts['treshini'][df_name]['crops'].append(int(c))
                        counts['brek'][df_name]['crops'] = list(df.breckchia.values[1:])
                        counts['miel'][df_name]['crops'] = list(df.milonit.values[1:])
                        counts['kat'][df_name]['crops'] = list(df.cataclasit.values[1:])

                    if df_name == "1.png":
                        inter = df.loc[1, 'interval']
                        pos = inter.find("-")
                        begin = float(inter[:pos])
                    if df_name == str(length - 1) + ".png":
                        inter = df.loc[len(df) - 1, 'interval']
                        pos = inter.find("-")
                        end = float(inter[pos + 1:])

                self.model.counts_stat[os.path.dirname(os.path.realpath(__file__)) +
                                       "\\projects\\" + project_id + "\\" + well + "\\" + box + "\\" + box] = {'begin' : begin, 'end' : end, 'counts' : counts}
        with open('db.json', 'w') as outfile:
            json.dump(self.model.projects, outfile)
        with open('counts.json', 'w') as outfile:
            json.dump(self.model.counts_stat, outfile)

        p = Project(self.parent, self.model, project_id)
        self.model.current_page.grid_forget()
        self.model.current_page = p.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


    def warnings(self, message):
        newWindow = ctk.CTkToplevel(self.parent)
        newWindow.geometry("350x350")
        newWindow.wm_attributes("-topmost", 1)
        newWindow.title(["Warning", "Ошибка"][self.parent.lang])
        photo_label = ctk.CTkLabel(newWindow, bg_color="grey95", text=['Error in project structure', 'Структура проекта не верна'][self.parent.lang])
        photo_label.place(relwidth=0.9, relheight=0.35, relx=0.06, rely=0.05)
        warn_label = ctk.CTkLabel(newWindow, bg_color="grey95", text = message)
        warn_label.place(relwidth=0.9, relheight=0.35, relx=0.06, rely=0.5)
        newWindow.mainloop()

    def new_project(self):
        new_project = NewProject(self.parent, self.model)
        self.model.current_page.grid_forget()
        self.model.current_page = new_project.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


class Projects:
    def __init__(self, parent, model):
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=home_color)
        self.model = model
        self.parent = parent
        self.projects_btns = []

        def create_buttons(command):
            return ctk.CTkButton(self.frame, font=("Arial", 14),
                                                        text=key,
                                                        text_color="grey25", fg_color="#6cdfff", command = lambda : self.open_project(command))
        if len(self.model.projects) != 0:
            for key, value in model.projects.items():
                self.projects_btns.append(create_buttons(key))

        for i in range(len(self.projects_btns)):
            self.projects_btns[i].place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.2 + i * 0.1)

    def open_project(self, project_id):
        frame = Project(self.parent, self.model, project_id)
        self.model.current_page = frame.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


class Settings:
    def __init__(self, parent, model):
        self.model = model
        self.parent = parent
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=home_color)
        self.r_var = ctk.BooleanVar()
        self.r_var.set(self.parent.lang)

        self.delete = ctk.CTkButton(self.frame, corner_radius=10, height=40, border_spacing=10,
                                       text=["Delete all", "Удалить все"][int(self.r_var.get())],
                                       fg_color = "#ff926e", text_color=("gray10", "gray90"),anchor="w",
                                       command=lambda: self.delete_all())
        self.delete.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.2)

        self.r1 = ctk.CTkRadioButton(self.frame, text='Русский',
                         variable=self.r_var, value=True, command=lambda : self.r_lang(True))
        self.r2 = ctk.CTkRadioButton(self.frame, text='English',
                         variable=self.r_var, value=False, command=lambda : self.r_lang(False))
        self.r1.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.5)
        self.r2.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.6)

    def r_lang(self, value):
        self.delete.configure(text = ["Delete all", "Удалить все"][int(self.r_var.get())])
        self.parent.change_lang(value)

    def delete_all(self):
        self.newW = ctk.CTk()
        self.newW.geometry('350x200')
        self.newW.title("Удаление")

        self.q = ctk.CTkLabel(self.newW, text=["Delete all?", "Вы уверены, \n что хотите удалить все проекты?"][self.r_var.get()],
                                                   compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.q.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.1)

        self.delete = ctk.CTkButton(self.newW, corner_radius=10, height=40, border_spacing=10,
                                    text=["Delete", "Удалить"][self.r_var.get()],
                                    fg_color="#ff926e", anchor="w", text_color= "black",
                                    command=lambda: self.delete_db())
        self.delete.place(relwidth=0.3, relheight=0.2, relx=0.1, rely=0.5)
        self.back = ctk.CTkButton(self.newW, corner_radius=10, height=40, border_spacing=10,
                                    text=["Cancel", "Отмена"][self.r_var.get()],
                                    fg_color="#6cdfff", anchor="w", text_color= "black",
                                    command = lambda : self.newW.destroy())
        self.back.place(relwidth=0.3, relheight=0.2, relx=0.5, rely=0.5)
        self.newW.mainloop()

    def delete_db(self):
        path = os.path.dirname(os.path.realpath(__file__)) + "\\projects\\"
        self.model.clear(path)
        with open('db.json', 'w') as outfile:
            json.dump({}, outfile)
        with open('counts.json', 'w') as outfile:
            json.dump({}, outfile)
        self.newW.destroy()


class Instructions:

    def __init__(self, parent, model):
        self.parent = parent
        self.text = ['''СОЗДАНИЕ ПРОЕКТА
            Для создания нового проекта -- кнопка "Новый проект". Проект не должен иметь пустое имя. При открытии проекта можно создать новую скважину. С
            права -- список уже существующих скважин. Скважина должна иметь непустое название и глубину в формате целого или дробного числа. 


            СКВАЖИНА
            При открытии скважины отображается список ящиков, над каждым ящиком в списке -- индикаторы состояния. Справа -- панель управления. Наверху панели 
            указаны название скважины и через дробь -- глубина. Глубину можно изменить, введя новое значение в поле. Возможно добавление нового ящика. 
            Кнопка "колонка" открывает геологическую колонку для скважины. Изначально колонка пустая и в ней отображается только глубина. 


            КЛАССИФИКАЦИЯ СКВАЖИНЫ
            При нажатии кнопки "классифицировать все" начнется обработка и классификация всех ящиков скважины. Если в скважине уже есть обработанные ящики 
            и необходимо загрузить новые, то будут обработаны только новые ящики. По мере обработки индикаторы будут загораться зеленым, и таким образом можно 
            будет отслеживать процесс обработки. После того, как классификация завершится, можно будет открыть каждый ящик и в геологической колонке отобразятся 
            их интервалы и статистика.


            ЯЩИК
            Каждый загруженный ящик должен иметь от 3 до 6 полосок керна, лежащих по горизонтали (можно больше, но тогда снизится качество 
            предсказания модели). На каждом ящике должна быть закреплена подпись вида "инт. 145.6 - 154.9" (числа любые) для того, чтобы алгоритм распознавал
            интервал. Если надписей нет, то алгоритм выставит глубину автоматически от 0 до 5 метров. Необходимо, чтобы ящик целиком попадал в кадр и 
            находился в плоскости камеры. Также желательно, чтобы снимок имел разрешение по вертикали больше 1000 и меньше 10000 пикселей, тогда качество 
            распознавания будет оптимальным. 
            Если ящик обработан в скважине, то при его открытии отобразится детализация -- каждая полоска керна, таблица 
            с интервалами и статистикой. При переключении между типами, на рисунке будут отображаться распознанные сегменты. При нажатии кнопки "сохранить 
            колонки", сохранятся полоски керна в исходном разрешении. Если ящик не был классифицирован, то при первом его открытии произойдет 
            деление на колонки и поиск интервала. Такой ящик не будет отображаться в скважине, как классифицированный, но будет отображаться в геологической 
            колонке с пустой статистикой. Чтобы классифицировать отдельный ящик, нужно нажать "классифицировать" внутри ящика. В таблице отображается статистика 
            в процентах. Чтобы редактировать таблицу, нужно кликнуть 2 раза. При нажатии кнопки "сохранить csv", сохранятся таблицы. В случае некорректного 
            распознавания интервалов можно отредактировать интервал.


            ГЕОЛОГИЧЕСКАЯ КОЛОНКА
            В колонке отображаются ящики, для которых найден интервал. В случае пересечения интервалов, ящики ранжируются по возрастанию начал интервалов и 
            отображаются последовательно. При этом загорается индикатор предупреждения. В случае выхода за указанную глубину, также высвечивается предупреждение.
            Поле "OPEN" -- кнопка открытия соответствующего ящика. Для этого необходимо кликнуть дважды на него.


            СОХРАНЕНИЕ И ЗАГРУЗКА ПРОЕКТА
            Чтобы была возможность загружать проект, необходимо сохранить каждую скважину. Для этого на странице со скважиной нужно нажать "сохранить скважину".
            Без этого проект не сохранится корректно! Для загрузки проекта нужно нажать кнопку "загрузить проект" и выбрать папку проекта. При добавлении все 
            проекты автоматически оказываются в папке projects в каталоге приложения. Туда же сохраняются скважины и изображения в соответствии с древовидной 
            структурой. Загружаемый проект должен иметь в точности такую же структуру, какая есть изначально у всех создаваемых проектов. При удалении каких-либо 
            файлов или изменении структуры загрузка может произойти некорректно.

            ''',
            ''' CREATING A PROJECT
      To create a new project, click the "New Project" button. The project must not have an empty name. When opening a project, you can create a new well. WITH
      rights -- list of existing wells. The well must have a non-empty name and be prescribed in a format or fractional number.
    
    
      WELL
      When the well was opened, a list of boxes was found, above each box in the list are status indicators. On the right is the control panel. Top panel
      indication of the name of the well and through the fraction - depth. The depth can be changed by entering a new value in the field. adding a new possible box.
      The button "column" opens a geological column for wells. the column is empty and only the depth is not shown in it.
    
    
      WELL CLASSIFICATION
      When recording the "classify all" button, let's start processing and classifying all the boxes in the well. If there are already processed boxes in the well
      and you need to upload new ones, then only new boxes will be processed. As processing progresses, the indicators will turn green, and thus you can
      will wait for processing. After the classification is completed, you can open each box and the geological column will display
      their intervals and statistics.


      BOX
      Each loaded should have from 3 to 6 core strips lying on the horizontal (more is possible, but then the quality of the box is reduced).
      model predictions). Each box must have a signature like "int. 145.6 - 154.9" (any numbers) in order for the algorithm to recognize
      interval. If there are no inscriptions, then the algorithm will automatically set from 0 to 5 meters. It is necessary that the coronavirus infection get into the frame and
      goes to opposite chambers. It is also desirable that the image has a vertical resolution of more than 1000 and less than 10000, then the image quality
      will usually be optimal.
      If the box is processed in the well, then when it is opened, the detail will be displayed - each strip of core, table
      with intervals and statistics. When switching between types, as shown in the figure, recognizable segments appear. When writing the save button
      columns", the core strips will be saved in the original resolution.
      division by columns and search interval. Such a box will not be in the well, like a secret one, but it will not be a secret
      column with empty statistics. In order to classify an individual box, you must configure the "classification" of the inner box. Entered statistics
      in percentages. To quickly process, you need to press 2 times. When you write the "save csv" button, the tables are saved. When
      increasing the interval, you can edit the interval.
    
    
      GEOLOGICAL COLUMN
      In the column for displaying the boxes for which the interval was found. If the intervals overlap, the boxes are ranked in ascending order of the start interval and
      sequential display. At the same time, the forecast lights up. If the specified setting is exceeded, a warning is also displayed.
      The "OPEN" field is the opening of a suitable box. To do this, click on it.
    
    
      SAVE AND LOAD A PROJECT
      To be able to design the project, it is necessary to save all the wells. To do this, on the page with the well, you must provide "save the well".
      Without this, the project will not save correctly! To load a project, use the "load project" option and select the project folder. When adding all
      projects are automatically placed in the projects folder in the application directory. There same wells and images in accordance with the tree
      structure. The uploaded project must have the same structure as all embedded projects. When removing any
      files or structure loading loading can be dangerous.'''][not self.parent.lang]

        self.parent = parent
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=home_color)
        self.text_label = ctk.CTkLabel(self.frame, text=self.text, fg_color="#F5FFFA")
        self.text_label.place(relwidth=0.9, relheight=0.9, relx=0.05, rely=0.05)
