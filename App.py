import customtkinter as ctk
from main_page import HomePage, Settings, Projects, Instructions
from tkinter import ttk
import model
import uuid
import os
import pyautogui
home_color = "#f5f2ff"
#home_color = "#FFFFE0"
nav_color = "#c6c6ff"
#nav_color = "#8B008B"
new_nav_color = "#F4A460"
hover_color = "#8c82be"
clicked_color = "#e5e3fc"

class PermissionDenied(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)
        self.model = model
        self.title("access denied")
        self.geometry("700x450")
        self.iconbitmap('25173.ico')
        self.config(bg=home_color)
        self.resizable(True, True)

        self.frame = ctk.CTkFrame(self, corner_radius=0, fg_color=nav_color)
        self.frame.place(relwidth=0.9, relheight=0.35, relx=0.06, rely=0.1)
        warn_label = ctk.CTkLabel(self.frame, bg_color="grey95", text='Permission denied.' + '\n' + 'Device not recognized', font=('Arial', 18))
        warn_label.place(relwidth=0.5, relheight=0.35, relx=0.25, rely=0.1)


class App(ctk.CTk):
    def __init__(self, model):
        ctk.CTk.__init__(self)
        self.model = model
        self.title("IGT")
        self.geometry("700x450")
        self.iconbitmap('iGeo-logo.ico')
        self.config(bg=home_color)
        self.resizable(True, True)
        self.current_open_nav = True
        self.lang = True
        #
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # self.width, self.heigth = pyautogui.size().width, pyautogui.size().height
        self.width, self.heigth = self.winfo_screenwidth(), self.winfo_screenheight()
        print(self.heigth)
        # создание панели навигации
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=nav_color)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1)

        self.btn_home = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                      text=['Main', "Главное меню"][int(self.lang)],
                                      fg_color=nav_color, text_color="gray10", hover_color=hover_color,
                                      image=model.home_image, anchor="w",
                                      command=lambda: self.navigation_button(HomePage))
        self.btn_home.grid(row=1, column=0, sticky="ew")

        self.btn_projects = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                          text=["Projects", "Проекты"][int(self.lang)],
                                          fg_color=nav_color, text_color=("gray10", "gray90"),
                                          hover_color=(hover_color, "gray30"),
                                          image=model.pr, anchor="w",
                                          command=lambda: self.navigation_button(Projects))
        self.btn_projects.grid(row=2, column=0, sticky="ew")

        self.btn_settings = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                          text=["Settings", "Настройки"][int(self.lang)],
                                          fg_color=nav_color, text_color=("gray10", "gray90"),
                                          hover_color=(hover_color, "gray30"),
                                          image=model.chat_image, anchor="w",
                                          command=lambda: self.navigation_button(Settings))
        self.btn_settings.grid(row=3, column=0, sticky="ew")

        self.btn_instr = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                       text=["Instruction", "Инструкция"][int(self.lang)],
                                       fg_color=nav_color, text_color=("gray10", "gray90"),
                                       hover_color=(hover_color, "gray30"),
                                       image=model.add_user_image, anchor="w",
                                       command=lambda: self.navigation_button(Instructions))
        self.btn_instr.grid(row=4, column=0, sticky="ew")

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text=["Welcome! ", "Добро пожаловать! "][int(self.lang)],
                                                   compound="left", font=ctk.CTkFont("Arial", 14), image=model.logo_image)
        self.navigation_frame_label.grid(row=0, column=0, pady=8, padx=5)

        self.close_open = ctk.CTkButton(self.navigation_frame, text='', image=model.close,
                                   fg_color="#E0FFFF",
                                   anchor="center", command=lambda: self.press_close_open())
        self.close_open.place(relwidth=0.1, relheight=0.2, relx=0.9, rely=0.4)

        self.navigation_button(HomePage)

    # переключение на панели навигации
    def navigation_button(self, type):
        self.btn_home.configure(fg_color=home_color if type == HomePage else nav_color)
        self.btn_settings.configure(fg_color=(home_color, "gray25") if type == Settings else nav_color)
        self.btn_instr.configure(fg_color=(home_color, "gray25") if type == Instructions else nav_color)
        self.btn_projects.configure(fg_color=(home_color, "gray25") if type == Projects else nav_color)
        try:
            self.model.current_page.grid_forget()
        except AttributeError:
            pass
        page = type(self, self.model)
        self.model.current_page = page.frame
        self.model.current_page.grid(row=0, column=1, sticky="nsew")


    def press_close_open(self):
        if self.current_open_nav:
            self.btn_home.configure(text='', anchor='center', width=30)
            self.btn_projects.configure(text='', anchor='center', width=30)
            self.btn_settings.configure(text='', anchor='center', width=30)
            self.btn_instr.configure(text='', anchor='center', width=30)
            self.navigation_frame_label.configure(text='', compound='center', width=30)
            self.close_open.place_forget()
            self.close_open.place(relwidth=0.3, relheight=0.15, relx=0.72, rely=0.4)
            self.close_open.configure(image=model.open)
            self.current_open_nav = False
        else:
            self.btn_home.configure(text=['Main', 'Главное меню'][self.lang], anchor='w')
            self.btn_projects.configure(text=['Projects', 'Проекты'][self.lang], anchor='w')
            self.btn_settings.configure(text=['Settings', 'Настройки'][self.lang], anchor='w')
            self.btn_instr.configure(text=['Instructions', 'Инструкции'][self.lang], anchor='w')
            self.navigation_frame_label.configure(text=['  Welcome!', '  Добро пожаловать!'][self.lang], compound='left')
            self.close_open.place_forget()
            self.close_open.place(relwidth=0.1, relheight=0.2, relx=0.9, rely=0.4)
            self.close_open.configure(image=model.close)
            self.current_open_nav = True

    def change_lang(self, value):
        self.btn_home.configure(text=['Main', 'Главное меню'][int(value)], anchor='w')
        self.btn_projects.configure(text=['Projects', 'Проекты'][int(value)], anchor='w')
        self.btn_settings.configure(text=['Settings', 'Настройки'][int(value)], anchor='w')
        self.btn_instr.configure(text=['Instructions', 'Инструкция'][int(value)], anchor='w')
        self.navigation_frame_label.configure(text=['  Welcome!', '  Добро пожаловать!'][int(value)], compound='left')
        self.lang = value

if __name__ == '__main__':
    mac = uuid.getnode()
    print(mac)
    file_path = os.path.dirname(os.path.realpath(__file__))
    with open(file_path + '\\pythontoolsfiles\\rgui728293473uipythontools21894.pub', 'r') as f:
        r = f.read()
    if r == '':
        with open(file_path + '\\pythontoolsfiles\\rgui728293473uipythontools21894.pub',
                  'w') as f:
            f.write(str(mac))
            model = model.Model()
            app = App(model)
            app.mainloop()
    else:
        if mac == int(r):
            model = model.Model()
            app = App(model)
        else:
            app = PermissionDenied()
        app.mainloop()
