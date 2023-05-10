import customtkinter as ctk
from tkinter import ttk
from projects_and_wells import NewProject, Project
home_color = "#f5f2ff"
nav_color = "#c6c6ff"
import json


class HomePage:
    def __init__(self, parent, model):
        self.model = model
        self.parent = parent
        # ctk.CTkFrame.__init__(self, parent, corner_radius=0, fg_color = home_color)
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color=home_color)
        self.new_project = ctk.CTkButton(self.frame, text="Новый проект", image=model.plus, compound="left",
                                         command=self.new_project)
        self.new_project.configure(fg_color="#6cdfff", text_color="black", corner_radius=20, width=175, height=50)
        self.new_project.place(relwidth=0.5, relheight=0.1, relx=0.2, rely=0.1)

        self.load_pr = ctk.CTkButton(self.frame, text="Загрузить проект", image=model.plus,
                                     compound="left", command=lambda: self.parent.navigation_button(Projects))
        self.load_pr.configure(fg_color="#6cdfff", text_color="black", corner_radius=20, width=150, height=50)
        self.load_pr.place(relwidth=0.5, relheight=0.1, relx=0.2, rely=0.25)

        self.text = ctk.CTkLabel(self.frame, font=("Comic Sans MS", 20, "bold"), text="Выберите проект")
        self.text.place(relwidth=0.5, relheight=0.1, relx=0.2, rely=0.4)

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
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=home_color)

        self.delete = ctk.CTkButton(self.frame, corner_radius=10, height=40, border_spacing=10,
                                       text="Удалить все",
                                       fg_color = "#ff926e", text_color=("gray10", "gray90"),anchor="w",
                                       command=lambda: self.delete_all())
        self.delete.place(relwidth=0.5, relheight=0.08, relx=0.2, rely=0.2)

    def delete_all(self):
        self.newW = ctk.CTk()
        self.newW.geometry('350x200')
        self.newW.title("Удаление")

        self.q = ctk.CTkLabel(self.newW, text="Вы уверены, \n что хотите удалить все?",
                                                   compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.q.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.1)

        self.delete = ctk.CTkButton(self.newW, corner_radius=10, height=40, border_spacing=10,
                                    text="Удалить",
                                    fg_color="#ff926e", anchor="w", text_color= "black",
                                    command=lambda: self.delete_db())
        self.delete.place(relwidth=0.3, relheight=0.2, relx=0.1, rely=0.5)
        self.back = ctk.CTkButton(self.newW, corner_radius=10, height=40, border_spacing=10,
                                    text="Отмена",
                                    fg_color="#6cdfff", anchor="w", text_color= "black",
                                    command = lambda : self.newW.destroy())
        self.back.place(relwidth=0.3, relheight=0.2, relx=0.5, rely=0.5)
        self.newW.mainloop()

    def delete_db(self):
        with open('db.json', 'w') as outfile:
            json.dump({}, outfile)
        self.newW.destroy()


class Instructions:
    def __init__(self, parent, model):
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=home_color)
