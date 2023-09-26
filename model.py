import os
from PIL import Image
import customtkinter as ctk
import json
import shutil

class Model():
    def __init__(self):
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "iGeo-logo.png")), size=(85, 65))
        self.large_test_image = ctk.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")),
                                             size=(500, 150))
        self.plus = ctk.CTkImage(Image.open(os.path.join(image_path, "1828921.png")), size=(15, 15))
        self.home_image = ctk.CTkImage(Image.open(os.path.join(image_path, "home_dark.png")), size=(20, 20))
        self.chat_image = ctk.CTkImage(Image.open(os.path.join(image_path, "settings_new.png")), size=(20, 20))
        self.add_user_image = ctk.CTkImage(Image.open(os.path.join(image_path, "2258853.png")), size=(20, 20))
        self.pr = ctk.CTkImage(Image.open(os.path.join(image_path, "chat_dark.png")), size=(20, 20))
        self.z = ctk.CTkImage(Image.open(os.path.join(image_path, "37403.png")), size=(18, 15))
        self.lupa = ctk.CTkImage(Image.open(os.path.join(image_path, "751463.png")), size=(12, 12))
        self.close = ctk.CTkImage(Image.open(os.path.join(image_path, "61032.png")), size=(10, 20))
        self.open = ctk.CTkImage(Image.open(os.path.join(image_path, "open.png")), size=(10, 20))
        self.heads = ['interval', 'well', 'box', 'cracks', 'kern', 'destroyed', 'veins', 'breckchia', 'cataclasit', 'milonit']

        self.current_page = 0
        with open(self.file_path + "\\db.json", 'r',
                  encoding='utf-8') as f:
            data = json.load(f)
        self.projects = data

        with open(self.file_path + "\\counts.json", 'r',
                  encoding='utf-8') as f:
            c = json.load(f)
        self.counts_stat = c


    def load_columns(self, path):
        column_dir = os.listdir(path)
        return column_dir

    def clear(self, path):
        dir = os.listdir(path)
        for files in dir:
            path1 = path + "\\" + files
            try:
                shutil.rmtree(path1)
            except OSError:
                os.remove(path1)


m = Model()
print(m.projects)