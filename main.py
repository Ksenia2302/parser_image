import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
from io import  BytesIO

class ImageParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Парсер изображений')
        self.root.geometry('800x600')
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text='URL страницы:').pack(pady=5)
        self.url_entry = ttk.Entry(self.root, width=60)
        self.url_entry.pack(pady=5)
        self.url_entry.insert(0, 'https://ya.ru')

        self.parse_btn = ttk.Button(self.root, text='Получить изображения', command=self.parse_images)
        self.parse_btn.pack(pady=5)


        self.imges_frame = ttk.Frame(self.root)
        self.imges_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


        self.canvas = tk.Canvas(self.imges_frame)

        self.scrollbar = ttk.Scrollbar(self.imges_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar_frame = ttk.Frame(self.canvas)

        self.scrollbar_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollbar_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)


        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right',fill='y')



    def parse_images(self):
        url = self.url_entry.get()
        if not url.startswith(('https://', 'http://')):
            url = 'https://' + url
        for widget in self.scrollbar_frame.winfo_children():
            widget.destroy()

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')

        if not img_tags:
            messagebox.showinfo('Информация', 'На странице не найдено изображений')
            return

        for i, img_tag in enumerate(img_tags):
            img_url = img_tag.get('src')
            if not img_url:
                continue

            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = url + img_url
            elif not img_url.startswith(('https://', 'http://')):
                img_url = url = '/' + img_url

            try:
                img_response = requests.get(img_url, stream=True)
                img_response.raise_for_status()

                img_data = Image.open(BytesIO(img_response.content))
                width, height = img_data.size
                max_size = 300
                if width > max_size or height > max_size:
                    ratio = min(max_size / width, max_size / height)
                    img_data = img_data.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)

                img_tk = ImageTk.PhotoImage(img_data)
                img_label = ttk.Label(self.scrollbar_frame, image=img_tk)
                img_label.image = img_tk
                img_label.pack(pady=2)

                url_label = ttk.Label(self.scrollbar_frame, text=img_url, wraplength=500)
                url_label.pack(pady=2)


            except Exception as e:
                print(e)


    def canvas(self):
        pass









root = tk.Tk()
i = ImageParserApp(root)

root.mainloop()
