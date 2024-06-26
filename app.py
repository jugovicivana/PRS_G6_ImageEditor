import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import multiprocessing
from multiprocessing import Pool
import time
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from tkinter import font
import psutil
import numpy as np
import tempfile
from tkinter import messagebox


# def rotate_block(block):
#     """ Rotira jedan blok slike za 90 stepeni """
#     return np.rot90(block)

def apply_color_filter_part(index, part, color):
    r, g, b = part.split()
    if color == 'red':
        r = r.point(lambda p: p * 1.5)
    elif color == 'green':
        g = g.point(lambda p: p * 1.5)
    elif color == 'blue':
        b = b.point(lambda p: p * 1.5)
    return index, Image.merge('RGB', (r, g, b))

def flip_image_part(index, part):
    return index, part.transpose(Image.FLIP_LEFT_RIGHT)

def blur_image_part(index, part):
    part = part.filter((ImageFilter.GaussianBlur(radius=8)))
    return index, part


def process_part( index, part):
    # Apply saturation enhancement to a part of the image
    enhancer = ImageEnhance.Color(part)
    processed_part = enhancer.enhance(1.5)
    return index, processed_part
 

def decrease_sat_part( index, part):
    # Apply saturation enhancement to a part of the image
    enhancer = ImageEnhance.Color(part)
    processed_part = enhancer.enhance(0.5)
    return index, processed_part

def complex_filter_part(index, part):
    # Povećanje zasićenja
    enhancer = ImageEnhance.Color(part)
    part = enhancer.enhance(1.5)

    # e1=ImageEnhance.Sharpness(part)
    # part=e1.enhance(2.0)

    # part=ImageOps.autocontrast(part)
    # part=ImageOps.posterize(part, bits=2)
    # Primena zamućenja
    part = part.filter(ImageFilter.BLUR)

    # Povećanje detalja
    part = part.filter(ImageFilter.DETAIL)

    # Poboljšanje ivica
    part = part.filter(ImageFilter.EDGE_ENHANCE_MORE)

    #Dodavanje dodatnih filtera za složenost
    # part = part.filter(ImageFilter.CONTOUR)
    part = part.filter(ImageFilter.SHARPEN)
    part=part.filter(ImageFilter.MedianFilter(size=3))

    return index, part



def complexBW_filter_part(index, part):

    part=part.convert("L")
    # Povećanje zasićenja
    enhancer = ImageEnhance.Contrast(part)
    part = enhancer.enhance(1.5)

    
    part = part.filter(ImageFilter.BLUR)

    # Povećanje detalja
    part = part.filter(ImageFilter.DETAIL)

    # Poboljšanje ivica
    part = part.filter(ImageFilter.EDGE_ENHANCE_MORE)

    part = part.filter(ImageFilter.SHARPEN)
    part=part.filter(ImageFilter.MedianFilter(size=3))

    return index, part


class StartPage:

    # def create_main_window(self):

    #     # self.main_window.geometry("400x300")
    def on_closing(self):
        self.root.destroy() 

    def add_button(self):
        # btn_open_page = ttk.Button(self.root, text="Otvori Image App", command=self.open_new_page)
        # btn_open_page.pack(pady=(100, 20))  # Gornji razmak 100 piksela, donji razmak 20 piksela

        # # Drugo dugme
        # btn_auto_process = ttk.Button(self.root, text="Automatski Izaberi Nacin Obrade", command=self.auto_select_processing)
        # btn_auto_process.pack(pady=20)  # Gornji i donji razmak 20 piksela

              # Dugme za otvaranje Image App (na levoj strani)
        # btn_open_page = ttk.Button(self.root, text="Manuelno biranje", command=self.open_new_page)
        # btn_open_page.pack(side=tk.RIGHT, padx=(20, 10), pady=(20, 10))  # Razmaci od 20 piksela sa leve i desne strane, 10 piksela gore i dole
        # # btn_open_page.grid(row=0, column=10)
        # # Dugme za automatski izbor načina obrade (na desnoj strani)
        # btn_auto_process = ttk.Button(self.root, text="Automatsko biranje", command=self.auto_select_processing)
        # btn_auto_process.pack(side=tk.RIGHT, padx=(10, 20), pady=(20, 10))  # Razmaci od 10 piksela sa leve i desne strane, 20 piksela gore i dole

        # Kreirajte stil za dugmad
        self.style = ttk.Style()
        self.style.configure("TButton", 
                             font=("Verdana", 10), 
                             foreground="#ea9999", 
                             background="#e06666", 
                             borderwidth=0, 
                             padding=6)
        self.style.map("TButton",
                       background=[("active", "#e06666")],
                       relief=[("pressed", "sunken")])

        self.canvas = tk.Canvas(self.root, width=self.background_image.width(), height=self.background_image.height())
        self.canvas.pack(fill="both", expand=True)
        
        # Postavite sliku kao pozadinu
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        # Dugme za manuelno biranje        
        btn_open_page = ttk.Button(self.root, text="Manuelno biranje", command=self.open_manual_page, style="TButton")         
        # btn_open_page.grid(row=4, column=0, padx=(20, 10), pady=(20, 10))             
        self.canvas.create_window(450, 150, anchor="w", window=btn_open_page)  # Postavite dugme na kanvasu

        # Dugme za automatski izbor načina obrade       
        btn_auto_process = ttk.Button(self.root, text="Automatsko biranje", command=self.auto_select_processing, style="TButton")         
        # btn_auto_process.grid(row=5, column=0, padx=(20, 10), pady=(20, 10))
        self.canvas.create_window(445, 250, anchor="w", window=btn_auto_process)  # Postavite dugme na kanvasu


    def auto_select_processing(self):
        # Dodajte ovde funkcionalnost za automatski izbor načina obrade
        print("Automatski izbor nacina obrade")
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("Automatsko izvrsavanje")
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.image_app = ImageUploaderApp(self.main_window, processing_mode) 
        # Dodajte elemente ili funkcionalnosti na novu stranicu
        self.root.withdraw()
        

    def open_manual_page(self):
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("Manuelno izvrsavanje")
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.image_app = ImageUploaderApp(self.main_window, "Manual") 
        # Dodajte elemente ili funkcionalnosti na novu stranicu
        self.root.withdraw()

    def add_artify_text(self):
        # Kreiranje fonta
        custom_font = font.Font(family="Lucida Handwriting", size=38, weight="bold")

        # Nacrtajte tekst na kanvasu
        self.canvas.create_text(330, 200, text="Artify", font=custom_font, fill="white", anchor="center")

    def __init__(self, root):
        self.root = root
        self.root.configure(bg='#F1E5D1')  # Postavi boju pozadine na lila
        self.root.resizable(False, False)

        icon = PhotoImage(file='icon.png')
        self.root.iconphoto(True, icon)
        # self.root.wm_attributes("-toolwindow", 1)
        #self.root.state('zoomed')
        window_width = 600
        window_height = 400

        # Dobavite širinu i visinu ekrana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Izračunajte x i y koordinate za centriranje prozora
        position_x = int(screen_width/2 - window_width/2)
        position_y = int(screen_height/2 - window_height/2)
        # Postavite geometriju prozora
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

     
            # Učitavanje slike za pozadinu
        self.background_image = tk.PhotoImage(file="pozNovo.png")

        # Postavljanje pozadine koristeći Label widget
        background_label = tk.Label(self.root, image=self.background_image)
        background_label.image = self.background_image  # Ovo je važno začuvanje reference na sliku
        background_label.place(x=0, y=0, relwidth=1, relheight=1)


        self.root.title(f"Artify")

        # label_artify = tk.Label(self.root, text="Artify", font=("Brush Script MT", 36), bg=self.root.cget("bg"), fg="black")
        # label_artify.pack(side=tk.RIGHT,pady=20)

        self.add_button()
        self.add_artify_text()

class ImageUploaderApp:

    def __init__(self, root, param):
        self.pool = multiprocessing.Pool(processes=psutil.cpu_count(logical=False))
        # print(self.pool)
        self.root = root
  # Maksimiziraj prozor da pokrije ekran osim trake sa zadacima
        self.root.configure(bg='#FFF8DC')  # Postavi boju pozadine na lila
        self.root.resizable(False, False)
        # self.root.wm_attributes("-toolwindow", 1)
        space=(" ")*220
        #self.root.state('zoomed')

        # icon = PhotoImage(file='icon.png')
        # self.root.iconphoto(False, icon)

        self.root.title(f"{space}Image Editor")
        icon= PhotoImage(file='icon.png')
        self.root.iconphoto(True, icon)
        # Dobavi širinu i visinu ekrana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
 
        # Izračunaj dimenzije za sliku tako da zauzima jednu trećinu visine ekrana
        image_width = screen_width // 3
        image_height = screen_height // 2

        
        window_width = 1500
        window_height = 740
        # Izračunajte x i y koordinate za centriranje prozora
        position_x = int(screen_width/2 - window_width/2-8)
        position_y = int(screen_height/2 - window_height/2-40)

        # Postavite geometriju prozora
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")




        # Kreiraj okvir za lijevu stranu (serijsko izvršavanje)
        self.left_frame = tk.Frame(root, bg='#FFF8DC')
        self.left_frame.pack(side='left', fill='both', expand=True)
        self.left_frame.pack_propagate(0) 
        label_serial = tk.Label(self.left_frame, text="Serijsko izvršavanje", bg='#FFF8DC', font=("Helvetica", 20), fg='#640D6B')
        label_serial.pack(side='top', pady=(10, 0))  # Postavljanje natpisa na vrh i centriranje horizontalno

        self.label_text=tk.Label(self.left_frame, text="", bg='#FFF8DC', font=("Helvetica", 14), fg='#640D6B')
        self.label_text.pack(side='bottom', pady=(0, 0))

        # Kreiraj okvir za desnu stranu (paralelno izvršavanje)
        self.right_frame = tk.Frame(root, bg='#FFF8DC')
        self.right_frame.pack(side='right', fill='both', expand=True)
        self.right_frame.pack_propagate(0) 
 
        # Kreiranje natpisa "Paralelno izvršavanje"
        label_parallel = tk.Label(self.right_frame, text="Paralelno izvršavanje", bg='#FFF8DC', font=("Helvetica", 20), fg='#B51B75')
        label_parallel.pack(side='top', pady=(10, 0))  # Postavljanje natpisa na vrh i centriranje horizontalno
        self.label_text_par=tk.Label(self.right_frame, text="", bg='#FFF8DC', font=("Helvetica", 14), fg='#640D6B')
        self.label_text_par.pack(side='bottom', pady=(0, 0))
 
        # Dodaj razmak između okvira
        #ttk.Separator(root, orient='vertical').pack(side='left', fill='y', padx=10)
        # Kreiranje stila za separator
        style = ttk.Style()
 
        # Postavljanje debljine i stila separatora
        style.configure("CustomSeparator.TSeparator", background='#EEA5A6', borderwidth=3, relief="sunken")
 
        # Kreiranje separatora sa postavljenim stilom
        separator = ttk.Separator(root, orient='vertical', style="CustomSeparator.TSeparator")
 
        # Postavljanje separatora
        separator.pack(side='left', fill='y', padx=10)
       
 
        # Funkcija za kreiranje okvira s Canvasom i teksturom slike
        def create_image_frame(parent_frame):
            image_frame = tk.Frame(parent_frame, bg='#EEA5A6', highlightbackground='#EEA5A6', highlightthickness=4)
            image_frame.pack(side='left', fill='none', expand=True, padx=10, pady=5)

            image_canvas = tk.Canvas(image_frame, width=image_width, height=image_height)
            image_canvas.pack(expand=True, fill='both')

            image1 = Image.open("slika1.png")
            photo1 = ImageTk.PhotoImage(image1)
            
            # Spremanje reference na PhotoImage kako bi se sačuvala od prikupljanja smeća
            image_canvas.image = photo1
            
            image_canvas.create_image(0, 0, anchor=tk.NW, image=photo1)

            image_canvas.create_text(image_width // 2, image_height // 2, text="Slika će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 20))
 
            return image_canvas
 
        # Kreiraj lijevi okvir za sliku i gumbe (serijsko izvršavanje)
        self.image_canvas = create_image_frame(self.left_frame)

        button_frame_canvas = tk.Canvas(self.left_frame, bg='#FFF8DC', highlightthickness=0)
        button_frame_canvas.pack(side='right', fill='y', expand=False)

 
        button_frame = tk.Frame(button_frame_canvas, bg='#FFF8DC')
        button_frame.pack(anchor='ne')  # Postavljamo anchor na 'ne' kako bismo postavili button_frame u gornji desni ugao button_frame_canvas

 
        button_frame.bind("<Configure>", lambda e: button_frame_canvas.configure(scrollregion=button_frame_canvas.bbox("all")))
 
        # Kreiraj gumbe i grupiraj ih po funkcionalnosti
        style = ttk.Style()
        style.configure("Main.TButton", font=("Helvetica", 10), padding=5, background='#D74B76',foreground='#EF9595')
        style.map("Main.TButton", background=[('active', '#EF9595')])
        style.map("Main.TButton", foreground=[('active', "#D74B76")])

        # Učitaj ikonu za Undo i Redo
        undo_icon = Image.open("undo.png")  # Promijenite naziv i putanju prema vašoj ikoni
        undo_icon = undo_icon.resize((20, 20), Image.LANCZOS)  # Prilagodi veličinu ikone koristeći LANCZOS filter
        undo_icon = ImageTk.PhotoImage(undo_icon)

        redo_icon = Image.open("redo.png")  # Promijenite naziv i putanju prema vašoj ikoni
        redo_icon = redo_icon.resize((20, 20), Image.LANCZOS)  # Prilagodi veličinu ikone koristeći LANCZOS filter
        redo_icon = ImageTk.PhotoImage(redo_icon)

        cut_icon = Image.open("cut.png")  # Promijenite naziv i putanju prema vašoj ikoni
        cut_icon = cut_icon.resize((20, 20), Image.LANCZOS)  # Prilagodi veličinu ikone koristeći LANCZOS filter
        cut_icon = ImageTk.PhotoImage(cut_icon)

        flip_icon = Image.open("flip.png")  # Promijenite naziv i putanju prema vašoj ikoni
        flip_icon = flip_icon.resize((20, 20), Image.LANCZOS)  # Prilagodi veličinu ikone koristeći LANCZOS filter
        flip_icon = ImageTk.PhotoImage(flip_icon)

        rotate_icon = Image.open("rotate.png")  # Promijenite naziv i putanju prema vašoj ikoni
        rotate_icon = rotate_icon.resize((20, 20), Image.LANCZOS)  # Prilagodi veličinu ikone koristeći LANCZOS filter
        rotate_icon = ImageTk.PhotoImage(rotate_icon)
 
        buttons_left = [
            ("Upload Image", self.upload_image),
            ("Reset Filters", self.reset_image),
            ("Save Image", self.save_image),
            ("Close Image", self.close_image),
            ("Increase Saturation", self.increase_saturation),
            ("Reduce Saturation", self.reduce_saturation)            
        ]
        
        style1 = ttk.Style()
        style1.configure("Complex.TButton", font=("Helvetica", 10), padding=5, background='#541be5',foreground='#674ea7')
        style1.map("Complex.TButton", background=[('active', '#674ea7')])
        style1.map("Complex.TButton", foreground=[('active', "#541be5")])


        buttons_complex_left= [
            ("Blur", self.blurr),
            ("Filter Colors", self.apply_complex_filter_serial),
            ("Filter BW", self.apply_complexBW_filter_serial)
        ]
 
        for text, command in buttons_left:
            button = ttk.Button(button_frame, text=text, command=command, width=18, style="Main.TButton")
            button.pack(pady=5)
        for text, command in buttons_complex_left:
            button = ttk.Button(button_frame, text=text, command=command, width=18, style="Complex.TButton")
            button.pack(pady=5)

        # Kreiraj okvir za cut/rotate
        cutrotate_frame_left = tk.Frame(button_frame, bg='#FFF8DC')
        cutrotate_frame_left.pack(pady=10)

        cut_button = ttk.Button(cutrotate_frame_left, image=cut_icon, command=self.start_crop)
        cut_button.image = cut_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        cut_button.pack(side='left', padx=5, pady=10)

        rotate_button = ttk.Button(cutrotate_frame_left, image=rotate_icon, command=self.rotate_image)
        rotate_button.image = rotate_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        rotate_button.pack(side='left', padx=5, pady=10)

        flip_button = ttk.Button(cutrotate_frame_left, image=flip_icon, command=self.flip)
        flip_button.image = flip_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        flip_button.pack(side='left', padx=5, pady=10)

        def on_enter_blue(event):
            event.widget.configure(bg='#99cff8', bd=1, width=7, fg="#034b81", relief=tk.SOLID)  # 


        def on_leave_blue(event):
            event.widget.configure(bg='#034b81', bd=1, fg="#99cff8",relief=tk.SOLID)  # 


        def on_enter_red(event):
            event.widget.configure(bg='#f88b83',width=7, fg="#ac1004", bd=1, relief=tk.SOLID)  # 


        def on_leave_red(event):
            event.widget.configure(bg='#ac1004', fg="#f88b83",bd=1, relief=tk.SOLID)  # 


        def on_enter_green(event):
            event.widget.configure(bg='#74fb3a', width=7, fg='#38761d',bd=1, relief=tk.SOLID)  # 


        def on_leave_green(event):
            event.widget.configure(bg='#38761d',fg='#74fb3a', bd=1, relief=tk.SOLID)  # 

        
        # Kreiraj okvir za boje (serijsko izvršavanje)
        color_frame_left = tk.Frame(button_frame, bg='#FFF8DC')
        color_frame_left.pack(pady=10)
 
        colors_left = [
            ("Blue", lambda: self.apply_color_filter('blue'), '#034b81', '#99cff8'),
            ("Red", lambda: self.apply_color_filter('red'), '#ac1004','#f88b83'),
            ("Green", lambda: self.apply_color_filter('green'), '#38761d', '#74fb3a')
        ]


        # background_colors = ["lightblue", "lightpink", "lightgreen"]
        # border_colors = ["blue", "red", "green"]
        # button_text=["Blue", "Red", "Green"]
        # commands = [lambda: self.apply_color_filter('blue'), lambda: self.apply_color_filter('red'), lambda: self.apply_color_filter('green')]


        # buttons = []
        # for i, (bg_color, border_color, txt) in enumerate(zip(background_colors, border_colors, button_text)):
        #     style_name = f"{i}.TButton"  # Jedinstveno ime za svaki stil
        #     style = ttk.Style()
        #     style.configure("Custom.TButton",
        #         font=("Helvetica", 10),
        #         padding=5,
        #         foreground='white')
        #     # Konfigurišite stil za svako dugme
        #     style.configure(style_name,
        #                     background=bg_color,
        #                     bordercolor=border_color,
        #                     relief="solid",
        #                     borderwidth=1
        #                     )
        #     style.map(style_name, background=[('active', bg_color)], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        #     # Kreirajte dugme sa odgovarajućim stilom
        #     button = ttk.Button(color_frame_left, text=txt, width=7,style=style_name)
        #     button.pack(side='left', padx=5)
        #     buttons.append(button)


        for text, command, color, fgText in colors_left:
            button = tk.Button(color_frame_left, text=text, command=command, width=7, bg=color,fg=fgText, bd=1)
            button.pack(side='left', padx=5)
            
            # Dodaj vezu za događaje miša
            if color == '#034b81':
                button.bind('<Enter>', on_enter_blue)
                button.bind('<Leave>', on_leave_blue)
            elif color == '#ac1004':
                button.bind('<Enter>', on_enter_red)
                button.bind('<Leave>', on_leave_red)
            elif color == '#38761d':
                button.bind('<Enter>', on_enter_green)
                button.bind('<Leave>', on_leave_green)


        # Kreiraj okvir za undo/redo 
        undoredo_frame_left = tk.Frame(button_frame, bg='#FFF8DC')
        undoredo_frame_left.pack(pady=10)
 
        # undoredo_left = [
        #     ("Undo", self.undo),
        #     ("Redo", self.redo)
        # ]

        undo_button = ttk.Button(undoredo_frame_left, image=undo_icon, command=self.undo)
        undo_button.image = undo_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        undo_button.pack(side='left', padx=5, pady=10)

        redo_button = ttk.Button(undoredo_frame_left, image=redo_icon, command=self.redo)
        redo_button.image = redo_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        redo_button.pack(side='left', padx=5, pady=10)
 
        # for text, command in undoredo_left:
        #     button = tk.Button(undoredo_frame_left, text=text, command=command, width=7,  background='#D74B76',foreground='#EF9595')
        #     button.pack(side='left', padx=5)
 
        # Kreiraj desni okvir za sliku i gumbe (paralelno izvršavanje)
        self.image_canvas_parallel = create_image_frame(self.right_frame)
 
        # Kreiraj okvir za gumbe s desne strane uz scrollbar
        button_frame_canvas_parallel = tk.Canvas(self.right_frame, bg='#FFF8DC', highlightthickness=0)
        button_frame_canvas_parallel.pack(side='right', fill='y', expand=False)
 
 
        button_frame_parallel = tk.Frame(button_frame_canvas_parallel, bg='#FFF8DC')
        button_frame_parallel.pack(anchor='ne')  # Postavljamo anchor na 'ne' kako bismo postavili button_frame_parallel u gornji desni ugao button_frame_canvas_parallel
 
        button_frame_parallel.bind("<Configure>", lambda e: button_frame_canvas_parallel.configure(scrollregion=button_frame_canvas_parallel.bbox("all")))
 
        # Kreiraj gumbe i grupiraj ih po funkcionalnosti
        buttons_right = [
            ("Upload Image", self.upload_image_parallel),
            ("Reset Filters", self.reset_image_parallel),
            ("Save Image", self.save_image_parallel),
            ("Close Image", self.close_image_parallel),
            ("Increase Saturation", lambda: self.increase_saturation_parallel(psutil.cpu_count(logical=False))),
            ("Reduce Saturation", lambda: self.reduce_saturation_parallel(psutil.cpu_count(logical=False))),
            
        ]

        style1 = ttk.Style()
        style1.configure("Complex.TButton", font=("Helvetica", 10), padding=5, background='#541be5',foreground='#674ea7')
        style1.map("Complex.TButton", background=[('active', '#674ea7')])
        style1.map("Complex.TButton", foreground=[('active', "#541be5")])


        buttons_complex_right= [
            ("Blur", self.blurr_parallel),
            ("Filter Colors", lambda:self.apply_complex_filter_parallel(psutil.cpu_count(logical=False))),
            ("Filter BW", lambda:self.apply_complexBW_filter_parallel(psutil.cpu_count(logical=False))),
        ]

 
        for text, command in buttons_right:
            button = ttk.Button(button_frame_parallel, text=text, command=command, width=18, style="Main.TButton")
            button.pack(pady=5)

        for text, command in buttons_complex_right:
            button = ttk.Button(button_frame_parallel, text=text, command=command, width=18, style="Complex.TButton")
            button.pack(pady=5)

        
         # Kreiraj okvir za cut/rotate
        cutrotate_frame_right = tk.Frame(button_frame_parallel, bg='#FFF8DC')
        cutrotate_frame_right.pack(pady=10)

        cut_button_parallel = ttk.Button(cutrotate_frame_right, image=cut_icon, command=self.start_crop_parallel)
        cut_button_parallel.image = cut_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        cut_button_parallel.pack(side='left', padx=5, pady=10)

        rotate_button_parallel = ttk.Button(cutrotate_frame_right, image=rotate_icon, command=self.rotate_image_parallel)
        rotate_button_parallel.image = rotate_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        rotate_button_parallel.pack(side='left', padx=5, pady=10)

        flip_button_parallel = ttk.Button(cutrotate_frame_right, image=flip_icon, command=self.flip_parallel)
        flip_button_parallel.image = flip_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        flip_button_parallel.pack(side='left', padx=5, pady=10)

         # Kreiraj okvir za boje
        color_frame_right = tk.Frame(button_frame_parallel, bg='#FFF8DC')
        color_frame_right.pack(pady=10)
 
        colors_right = [
             ("Blue", lambda: self.apply_color_filter_parallel('blue'), '#034b81', '#99cff8'),
            ("Red", lambda: self.apply_color_filter_parallel('red'), '#ac1004','#f88b83'),
            ("Green", lambda: self.apply_color_filter_parallel('green'), '#38761d', '#74fb3a')
        ]
 
        for text, command, color, fgText in colors_right:
            button = tk.Button(color_frame_right, text=text, command=command, width=7, bg=color,fg=fgText, bd=1)
            button.pack(side='left', padx=5)
            
            # Dodaj vezu za događaje miša
            if color == '#034b81':
                button.bind('<Enter>', on_enter_blue)
                button.bind('<Leave>', on_leave_blue)
            elif color == '#ac1004':
                button.bind('<Enter>', on_enter_red)
                button.bind('<Leave>', on_leave_red)
            elif color == '#38761d':
                button.bind('<Enter>', on_enter_green)
                button.bind('<Leave>', on_leave_green)


         # Kreiraj okvir za undo/redo 
        undoredo_frame_right = tk.Frame(button_frame_parallel, bg='#FFF8DC')
        undoredo_frame_right.pack(pady=10)


        undo_button_parallel = ttk.Button(undoredo_frame_right, image=undo_icon, command=self.undo_parallel)
        undo_button_parallel.image = undo_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        undo_button_parallel.pack(side='left', padx=5, pady=10)

        redo_button_parallel = ttk.Button(undoredo_frame_right, image=redo_icon, command=self.redo_parallel)
        redo_button_parallel.image = redo_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        redo_button_parallel.pack(side='left', padx=5, pady=10)
 
        
        # Inicijalizacija slike i povijesti za serijsko izvršavanje
        self.image = None
        self.image_history = []
        self.history_index = -1
 
        # Inicijalizacija slike i povijesti za paralelno izvršavanje
        self.image_parallel = None
        self.image_history_parallel = []
        self.history_index_parallel = -1

        if(param=="Parallel"):
            self.left_frame.destroy()
        elif(param=="Serial"):
            self.right_frame.destroy()
 
 
    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.image_history = [self.image.copy()]
            imgwidth=self.image.width
            imgheight=self.image.height

            self.history_index = 0
            self.display_image()
            self.label_text.config(text=f"Dimenzije slike {imgwidth}x{imgheight}.")

 
    def upload_image_parallel(self): # ADDED
        file_path = filedialog.askopenfilename() # ADDED
        if file_path: # ADDED
            self.image_parallel = Image.open(file_path) # ADDED
            self.image_history_parallel = [self.image_parallel.copy()] # ADDED

            imgwidth=self.image_parallel.width
            imgheight=self.image_parallel.height

            self.history_index_parallel = 0 # ADDED
            self.display_image_parallel() # ADDED
            self.label_text_par.config(text=f"Dimenzije slike {imgwidth}x{imgheight}.")

 
    def display_image(self):
        if self.image:
            img=self.image
            self.image_canvas.delete("all")
            image_width=self.root.winfo_width()//3
            # Prilagodite veličinu slike na temelju širine image_canvas
            if(img.height<=img.width):
                imgratio = img.height / img.width
               
                img = img.resize((image_width, int(image_width * imgratio)))
                canvas_width = img.width
                canvas_height =int(canvas_width * imgratio)
            else:
                imgratio = img.width / img.height
                img = img.resize((int(image_width * imgratio),image_width))
                canvas_height = img.height
                canvas_width =int(canvas_height * imgratio)
 
         
            self.image_canvas.config(width=canvas_width, height=canvas_height)
 
            # Set the image in the center of the canvas
            image_width, image_height =img.size
            x_offset = (canvas_width - image_width) / 2
            y_offset = (canvas_height - image_height) / 2
            self.photo = ImageTk.PhotoImage(img)
 
            self.image_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)
 
 
    def close_image(self):
        if self.image:
            self.image_canvas.delete("all")    

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
 
            # Izračunaj dimenzije za sliku tako da zauzima jednu trećinu visine ekrana
            image_width = screen_width // 3
            image_height = screen_height // 2

            self.image_canvas.config(width=image_width, height=image_height)

            self.image_canvas.pack(expand=True, fill='both')

            image1 = Image.open("slika1.png")
            photo1 = ImageTk.PhotoImage(image1)
            
            # Spremanje reference na PhotoImage kako bi se sačuvala od prikupljanja smeća
            self.image_canvas.image = photo1
            
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=photo1)


            self.image_canvas.create_text(image_width // 2, image_height // 2, text="Slika će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 20))



            self.label_text.config(text="Slika uklonjena")
            # self.history_index=-1
            self.history_index=0
            self.image_history = [None]


    def close_image_parallel(self):
        if self.image_parallel:
            self.image_canvas_parallel.delete("all")    
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
 
            # Izračunaj dimenzije za sliku tako da zauzima jednu trećinu visine ekrana
            image_width = screen_width // 3
            image_height = screen_height // 2

            self.image_canvas_parallel.config(width=image_width, height=image_height)


            self.image_canvas_parallel.pack(expand=True, fill='both')

            image1 = Image.open("slika1.png")
            photo1 = ImageTk.PhotoImage(image1)
            
            # Spremanje reference na PhotoImage kako bi se sačuvala od prikupljanja smeća
            self.image_canvas_parallel.image = photo1
            
            self.image_canvas_parallel.create_image(0, 0, anchor=tk.NW, image=photo1)


            self.image_canvas_parallel.create_text(image_width // 2, image_height // 2, text="Slika će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 20))
            self.label_text_par.config(text="Slika uklonjena")

            self.history_index_parallel=0
            self.image_history_parallel = [None]



    def display_image_parallel(self): # ADDED
        if self.image_parallel:
            img=self.image_parallel
            self.image_canvas_parallel.delete("all")
            image_width=self.root.winfo_width()//3
 
            # Prilagodite veličinu slike na temelju širine image_canvas
            if(img.height<=img.width):
                imgratio = img.height / img.width
                img = img.resize((image_width, int(image_width * imgratio)))

                canvas_width = img.width
                canvas_height =int(canvas_width * imgratio)
            else:
                imgratio = img.width / img.height
                img = img.resize((int(image_width * imgratio),image_width))
                canvas_height = img.height
                canvas_width =int(canvas_height * imgratio)
         
            self.image_canvas_parallel.config(width=canvas_width, height=canvas_height)
 
            # Set the image in the center of the canvas
            image_width, image_height =img.size
            x_offset = (canvas_width - image_width) / 2
            y_offset = (canvas_height - image_height) / 2
            self.photo_parallel = ImageTk.PhotoImage(img)
 
            self.image_canvas_parallel.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo_parallel)
 
    def reset_image(self):
        if self.image_history:
            self.image = self.image_history[0]
            self.history_index = 0
            self.display_image()
            if self.image:
                self.label_text.config(text="Filteri resetovani")

 
    def reset_image_parallel(self): # ADDED
        if self.image_history_parallel: # ADDED
            self.image_parallel = self.image_history_parallel[0] # ADDED
            self.history_index_parallel = 0 # ADDED
            self.display_image_parallel() # ADDED
            if self.image_parallel:
                self.label_text_par.config(text="Filteri resetovani")

 
    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.image.save(file_path)
                self.label_text.config(text=f"Slika {file_path} je sačuvana")
                messagebox.showinfo("Obavještenje", f"Slika je sačuvana na lokaciju {file_path}")
 
    def save_image_parallel(self): # ADDED
        if self.image_parallel: # ADDED
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]) # ADDED
            if file_path: # ADDED
                self.image_parallel.save(file_path) # ADDED
                self.label_text_par.config(text=f"Slika {file_path} je sačuvana")
                messagebox.showinfo("Obavještenje", f"Slika je sačuvana na lokaciju {file_path}")

 
    def increase_saturation(self):
        if self.image:
            start_time = time.time()  # Start timing
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(1.5)
            end_time = time.time()  # End timing
            duration = end_time - start_time
            # print(f"Time taken to apply saturation serial: {duration:.4f} seconds")
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            self.update_history()
            self.display_image()
 
 
    def enhance_color(self, image_part, factor):
        # Obrada dela slike
        enhancer = ImageEnhance.Color(image_part)
        processed_part = enhancer.enhance(factor)
        return processed_part
 
 
    def increase_saturation_parallel(self, num_parts):
        if not self.image_parallel:
            return

        # Podelite sliku na delove sa indeksima
        overlap = 10  # Ili neki drugi broj piksela za preklapanje
        # Podelite sliku na delove sa indeksima
        image_parts_with_indices = self.split_image(num_parts, overlap)

        part_height = self.image_parallel.size[1] // num_parts

        start_time = time.time()  # Start timing

        # Obrada svakog dela paralelno
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_part, index, part) for index, part in image_parts_with_indices]

            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())

        # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
        processed_parts.sort(key=lambda x: x[0])
        processed_parts = [part for index, part in processed_parts]

        # Spajanje obrađenih delova u jednu sliku
        self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)

        end_time = time.time()  # End timing
        duration = end_time - start_time
        # print(f"Time taken to apply saturation parallel: {duration:.4f} seconds")
        
        self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
        # Ažurirajte istoriju i prikažite finalnu sliku
        self.update_history_parallel()
        self.display_image_parallel()

    def split_image(self, num_parts, overlap=10):
        width, height = self.image_parallel.size
        part_height = height // num_parts
        image_parts_with_indices = []

        for i in range(num_parts):
            upper = max(0, i * part_height - overlap)
            lower = min(height, (i + 1) * part_height + overlap)
            part = self.image_parallel.crop((0, upper, width, lower))
            # print(f"Part {i}: upper={upper}, lower={lower}")
            image_parts_with_indices.append((i, part))

        return image_parts_with_indices
    
    def merge_image_parts(self, image_parts, part_height, overlap):
        if not image_parts:
            return None

        width = image_parts[0].size[0]
        total_height = part_height * len(image_parts)
        merged_image = Image.new("RGB", (width, total_height))

        for i, part in enumerate(image_parts):
            if i == 0:
                merged_image.paste(part.crop((0, 0, width, part_height + overlap)), (0, i * part_height))
            elif i == len(image_parts) - 1:
                merged_image.paste(part.crop((0, overlap, width, part.size[1])), (0, i * part_height))
            else:
                merged_image.paste(part.crop((0, overlap, width, part_height + overlap)), (0, i * part_height))
            # print(f"Part {i} pasted at: {i * part_height}")

        return merged_image



 
    def reduce_saturation(self):
        if self.image:
            start_time = time.time()  # Start timing
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(0.5)
            end_time = time.time()  # End timing
            duration = end_time - start_time
            # print(f"Time taken to apply saturation serial: {duration:.4f} seconds")
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            self.update_history()
            self.display_image()
 
    def reduce_saturation_parallel(self, num_parts): # ADDED
        if self.image_parallel: # ADDED
            # enhancer = ImageEnhance.Color(self.image_parallel) # ADDED
            # self.image_parallel = enhancer.enhance(0.5) # ADDED
            # self.update_history_parallel() # ADDED
            # self.display_image_parallel() # ADDED

            overlap = 10  
            # Podelite sliku na delove sa indeksima
            image_parts_with_indices = self.split_image(num_parts, overlap)

            part_height = self.image_parallel.size[1] // num_parts

            start_time = time.time()  # Start timing

            # Obrada svakog dela paralelno
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(decrease_sat_part, index, part) for index, part in image_parts_with_indices]

                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            # Spajanje obrađenih delova u jednu sliku
            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)

            end_time = time.time()  # End timing
            duration = end_time - start_time
            # print(f"Time taken to reduce saturation parallel: {duration:.4f} seconds")
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            # Ažurirajte istoriju i prikažite finalnu sliku
            self.update_history_parallel()
            self.display_image_parallel()
        else:
            return
    def apply_complex_filter_serial(self):
        if not self.image:
            return
        start_time = time.time()

      
        # Povećanje zasićenja
        enhancer = ImageEnhance.Color(self.image)
        self.image = enhancer.enhance(1.5)

        # Primena zamućenja
        self.image = self.image.filter(ImageFilter.BLUR)

        # Povećanje detalja
        self.image = self.image.filter(ImageFilter.DETAIL)

        # # Poboljšanje ivica
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        self.image = self.image.filter(ImageFilter.SHARPEN)

        self.image=self.image.filter(ImageFilter.MedianFilter(size=3))

        #----------------------------------
        # e1=ImageEnhance.Sharpness(self.image)
        # self.image=e1.enhance(2.0)

        # self.image=ImageOps.autocontrast(self.image)
        # self.image=ImageOps.posterize(self.image, bits=2)

        end_time = time.time()
        duration = end_time - start_time
        # print(f"Time taken to apply complex filter serial: {duration:.4f} seconds")
        self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
        self.update_history()
        self.display_image()
    def apply_complexBW_filter_serial(self):
        if not self.image:
            return
        start_time = time.time()

        # Pretvaranje slike u crno-bijelu
        self.image = self.image.convert("L")

        # Podešavanje kontrasta
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(1.5)

        # Primjena filtera za zamućenje
        self.image = self.image.filter(ImageFilter.BLUR)

        # Primjena filtera za detalje
        self.image = self.image.filter(ImageFilter.DETAIL)

        # Poboljšanje ivica
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # Oštrina
        self.image = self.image.filter(ImageFilter.SHARPEN)

        # Filter za medijan
        self.image = self.image.filter(ImageFilter.MedianFilter(size=3))

        end_time = time.time()
        duration = end_time - start_time
        # print(f"Time taken to apply complex BW filter serial: {duration:.4f} seconds")
        self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
        self.update_history()
        self.display_image()
    def apply_complex_filter_parallel(self, num_parts):
        if not self.image_parallel:
            return

        # Podelite sliku na delove sa indeksima
        overlap = 10  # Ili neki drugi broj piksela za preklapanje
        image_parts_with_indices = self.split_image(num_parts, overlap)

        part_height = self.image_parallel.size[1] // num_parts

        start_time = time.time()  # Start timing

        # Obrada svakog dela paralelno
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(complex_filter_part, index, part) for index, part in image_parts_with_indices]

            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())

        # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
        processed_parts.sort(key=lambda x: x[0])
        processed_parts = [part for index, part in processed_parts]

        # Spajanje obrađenih delova u jednu sliku
        self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
        
        end_time = time.time()  # End timing
        duration = end_time - start_time
        self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")

        # Ažurirajte istoriju i prikažite finalnu sliku
        self.update_history_parallel()
        self.display_image_parallel()

    def apply_complexBW_filter_parallel(self, num_parts):
        if not self.image_parallel:
            return

        # Podelite sliku na delove sa indeksima
        overlap = 10  # Ili neki drugi broj piksela za preklapanje
        image_parts_with_indices = self.split_image(num_parts, overlap)

        part_height = self.image_parallel.size[1] // num_parts

        start_time = time.time()  # Start timing

        # Obrada svakog dela paralelno
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(complexBW_filter_part, index, part) for index, part in image_parts_with_indices]

            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())

        # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
        processed_parts.sort(key=lambda x: x[0])
        processed_parts = [part for index, part in processed_parts]

        # Spajanje obrađenih delova u jednu sliku
        self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
        
        end_time = time.time()  # End timing
        duration = end_time - start_time
        self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")

        # Ažurirajte istoriju i prikažite finalnu sliku
        self.update_history_parallel()
        self.display_image_parallel()

 
    def apply_color_filter(self, color):
        if self.image:

            start_time = time.time()  # Start timing

            r, g, b = self.image.split()
            if color == 'red':
                r = r.point(lambda p: p * 1.5)
            elif color == 'green':
                g = g.point(lambda p: p * 1.5)
            elif color == 'blue':
                b = b.point(lambda p: p * 1.5)
            self.image = Image.merge('RGB', (r, g, b))


            end_time = time.time()  # End timing
            duration = end_time - start_time
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            self.update_history()
            self.display_image()
 
    def apply_color_filter_parallel(self, color):
        if self.image_parallel:
            # Podelite sliku na delove
            num_parts = psutil.cpu_count(logical=False) # Ovo možete prilagoditi prema broju dostupnih CPU jezgara
            overlap = 10
            image_parts_with_indices = self.split_image(num_parts, overlap)

            part_height = self.image_parallel.size[1] // num_parts

            start_time = time.time()  # Start timing

            # Obrada svakog dela paralelno
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(apply_color_filter_part, index, part, color) for index, part in image_parts_with_indices]

                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            # Spajanje obrađenih delova u jednu sliku
            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
            
            end_time = time.time()  # End timing
            duration = end_time - start_time
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            
            # Ažuriranje istorije i prikazivanje finalne slike
            self.update_history_parallel()
            self.display_image_parallel()
 
 
    def rotate_image(self):
        if self.image:
            img=self.image
            img = img.transpose(Image.ROTATE_90)
            self.image=img
            self.update_history() 
            self.display_image()
            self.label_text.config(text="Slika rotirana za 90 stepeni")
    # def merge_image_rot(self, image_parts, part_height, overlap):
    #     if not image_parts:
    #         return None

    #     width = image_parts[0].size[0]
    #     total_height = part_height * len(image_parts)
    #     merged_image = Image.new("RGB", (width, total_height))

    #     for i, part in enumerate(image_parts):
    #         if i == 0:
    #             merged_image.paste(part.crop((0, 0, width, part_height + overlap)), (0, i * part_height))
    #         elif i == len(image_parts) - 1:
    #             merged_image.paste(part.crop((0, overlap, width, part.size[1])), (0, i * part_height))
    #         else:
    #             merged_image.paste(part.crop((0, overlap, width, part_height + overlap)), (0, i * part_height))

    #     return merged_image
    def rotate_image_parallel(self): # ADDED

         if self.image_parallel:
            img=self.image_parallel
            img = img.transpose(Image.ROTATE_90)
            self.image_parallel=img
            self.update_history_parallel() 
            self.display_image_parallel()
            self.label_text_par.config(text="Slika rotirana za 90 stepeni")
        # if self.image_parallel: # ADDED
        #     self.image_parallel = self.image_parallel.rotate(90,resample=Image.LANCZOS, expand=True) # ADDED
        #     self.update_history_parallel() # ADDED
        # Otvori sliku i konvertuj je u numpy array
    #     angle=90
    #     num_processes=psutil.cpu_count(logical=False)
    #     img_array = np.array(self.image_parallel)
    #     # Odredi dimenzije slike
    # # Odredi dimenzije slike
    #     height, width, channels = img_array.shape
    #     # Podeli sliku na blokove (npr. 4 bloka)
    #     num_blocks = int(np.sqrt(num_processes))
    #     block_height = height // num_blocks
    #     block_width = width // num_blocks
    #     # Kreiraj listu blokova
    #     blocks = []
    #     for i in range(num_blocks):
    #         for j in range(num_blocks):
    #             block = img_array[i * block_height:(i + 1) * block_height, j * block_width:(j + 1) * block_width]
    #             blocks.append(block)
    #     # Koristi multiprocessing za paralelnu rotaciju blokova
    #     with multiprocessing.Pool(num_processes) as pool:
    #         rotated_blocks = pool.map(rotate_block, blocks)
    #     # Sastavi rotirane blokove nazad u jednu sliku
    #     rotated_image = np.zeros((width, height, channels), dtype=img_array.dtype)
    #     for i in range(num_blocks):
    #         for j in range(num_blocks):
    #             rotated_block = rotated_blocks[i * num_blocks + j]
    #             rotated_block_height, rotated_block_width, _ = rotated_block.shape
    #             rotated_image[j * rotated_block_width:(j + 1) * rotated_block_width, (num_blocks - i - 1) * rotated_block_height:(num_blocks - i) * rotated_block_height] = rotated_block
    #     # Konvertuj nazad u Image objekat i sačuvaj
    #     self.image_parallel = Image.fromarray(rotated_image)
    #     self.display_image_parallel()
 
    def start_crop(self):
        if self.image:
            self.image_canvas.bind("<ButtonPress-1>", self.on_crop_button_press)
            self.image_canvas.bind("<B1-Motion>", self.on_crop_button_move)
            self.image_canvas.bind("<ButtonRelease-1>", self.on_crop_button_release)
 
    def start_crop_parallel(self):
        if self.image_parallel:
            self.image_canvas_parallel.bind("<ButtonPress-1>", self.on_crop_button_press_parallel)
            self.image_canvas_parallel.bind("<B1-Motion>", self.on_crop_button_move_parallel)
            self.image_canvas_parallel.bind("<ButtonRelease-1>", self.on_crop_button_release_parallel)


    def on_crop_button_press(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        self.crop_rectangle = self.image_canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_start_x, self.crop_start_y, outline='red')
 
    
    def on_crop_button_press_parallel(self, event):
        self.crop_start_x_parallel = event.x
        self.crop_start_y_parallel = event.y
        self.crop_rectangle_parallel = self.image_canvas_parallel.create_rectangle(self.crop_start_x_parallel, self.crop_start_y_parallel, self.crop_start_x_parallel, self.crop_start_y_parallel, outline='red')


 
    def on_crop_button_move(self, event):
        curX, curY = (event.x, event.y)
        self.image_canvas.coords(self.crop_rectangle, self.crop_start_x, self.crop_start_y, curX, curY)
 
    def on_crop_button_move_parallel(self, event):
        curX, curY = (event.x, event.y)
        self.image_canvas_parallel.coords(self.crop_rectangle_parallel, self.crop_start_x_parallel, self.crop_start_y_parallel, curX, curY)


 
    def on_crop_button_release(self, event):
        self.crop_end_x, self.crop_end_y = (event.x, event.y)
        self.image_canvas.unbind("<ButtonPress-1>")
        self.image_canvas.unbind("<B1-Motion>")
        self.image_canvas.unbind("<ButtonRelease-1>")
        self.crop_image()
 
    def on_crop_button_release_parallel(self, event):
        self.crop_end_x_parallel, self.crop_end_y_parallel = (event.x, event.y)
        self.image_canvas_parallel.unbind("<ButtonPress-1>")
        self.image_canvas_parallel.unbind("<B1-Motion>")
        self.image_canvas_parallel.unbind("<ButtonRelease-1>")
        self.crop_image_parallel()
 
    def crop_image(self):
        if self.image:
            start_time = time.time()  # Start timing

            original_width, original_height = self.image.size
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
           
            scale_x = original_width / canvas_width
            scale_y = original_height / canvas_height
           
            crop_start_x = int(self.crop_start_x * scale_x)
            crop_start_y = int(self.crop_start_y * scale_y)
            crop_end_x = int(self.crop_end_x * scale_x)
            crop_end_y = int(self.crop_end_y * scale_y)
           
            # Izrezivanje slike sa transformisanim koordinatama
            cropped_image = self.image.crop((crop_start_x, crop_start_y, crop_end_x, crop_end_y))
            self.image = cropped_image

            width=self.image.width
            height=self.image.height

            end_time = time.time()  # End timing
            duration = end_time - start_time

            self.label_text.config(text=f"Dimenzija isječene slike {width}x{height}")
            
            self.update_history()
            self.display_image()
 
    def crop_image_parallel(self):
        if self.image_parallel:
            start_time = time.time()  # Start timing

            original_width, original_height = self.image_parallel.size
            canvas_width = self.image_canvas_parallel.winfo_width()
            canvas_height = self.image_canvas_parallel.winfo_height()
        
            scale_x = original_width / canvas_width
            scale_y = original_height / canvas_height
        
            crop_start_x = int(self.crop_start_x_parallel * scale_x)
            crop_start_y = int(self.crop_start_y_parallel * scale_y)
            crop_end_x = int(self.crop_end_x_parallel * scale_x)
            crop_end_y = int(self.crop_end_y_parallel * scale_y)
        
            cropped_image = self.image_parallel.crop((crop_start_x, crop_start_y, crop_end_x, crop_end_y))
            self.image_parallel = cropped_image

            width=self.image_parallel.width
            height=self.image_parallel.height

            end_time = time.time()  # End timing
            duration = end_time - start_time

            self.label_text_par.config(text=f"Dimenzija isječene slike {width}x{height}")

            self.update_history_parallel()
            self.display_image_parallel()

    # def crop_image_process(self, crop_start_x, crop_start_y, crop_end_x, crop_end_y, output_queue):
    #     with self.image_parallel as img:
    #         cropped_image = img.crop((crop_start_x, crop_start_y, crop_end_x, crop_end_y))
    #         with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
    #             cropped_image.save(temp_file.name)
    #             output_queue.put(temp_file.name)
 
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.image_history[self.history_index]
            self.display_image()
            self.label_text.config(text="Undo akcija izvršena")
 
    def undo_parallel(self): # ADDED
        if self.history_index_parallel > 0: # ADDED
            self.history_index_parallel -= 1 # ADDED
            self.image_parallel = self.image_history_parallel[self.history_index_parallel] # ADDED
            self.display_image_parallel() # ADDED
            self.label_text_par.config(text="Undo akcija izvršena")

 
    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.image = self.image_history[self.history_index]
            self.display_image()
            self.label_text.config(text="Redo akcija izvršena")

 
    def redo_parallel(self): # ADDED
        if self.history_index_parallel < len(self.image_history_parallel) - 1: # ADDED
            self.history_index_parallel += 1 # ADDED
            self.image_parallel = self.image_history_parallel[self.history_index_parallel] # ADDED
            self.display_image_parallel() # ADDED
            self.label_text.config(text="Redo akcija izvršena")

 
    def update_history(self):
        self.image_history = self.image_history[:self.history_index + 1]
        self.image_history.append(self.image.copy())
        self.history_index += 1
 
    def update_history_parallel(self): # ADDED
        self.image_history_parallel = self.image_history_parallel[:self.history_index_parallel + 1] # ADDED
        self.image_history_parallel.append(self.image_parallel.copy()) # ADDED
        self.history_index_parallel += 1 # ADDED
 
    def flip(self):
        if(self.image):
            start_time = time.time()  # Start timing
            self.image = self.image.transpose((Image.FLIP_LEFT_RIGHT))
            
            end_time = time.time()  # End timing
            duration = end_time - start_time
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            self.update_history()
            self.display_image()
 
    def flip_parallel(self):
        if self.image_parallel:
            # Podelite sliku na delove
            num_parts = psutil.cpu_count(logical=False)  # Ovo možete prilagoditi prema broju dostupnih CPU jezgara
            overlap = 10
            image_parts_with_indices = self.split_image(num_parts, overlap)

            part_height = self.image_parallel.size[1] // num_parts

            start_time = time.time()  # Start timing

            # Obrada svakog dela paralelno
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(flip_image_part, index, part) for index, part in image_parts_with_indices]

                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            # Spajanje obrađenih delova u jednu sliku
            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
            
            end_time = time.time()  # End timing
            duration = end_time - start_time
            # print(f"Time taken to apply flip parallel: {duration:.4f} seconds")
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")


            # Ažuriranje istorije i prikazivanje finalne slike
            self.update_history_parallel()
            self.display_image_parallel()

    def blurr(self):
        if(self.image):
            start_time = time.time()  # Start timing
            self.image = self.image.filter((ImageFilter.GaussianBlur(radius=8)))
            end_time = time.time()  # End timing
            duration = end_time - start_time
            self.update_history()
            self.display_image()
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
 
    def blurr_parallel(self):
        if self.image_parallel:
            # Podelite sliku na delove
            num_parts = psutil.cpu_count(logical=False)  # Ovo možete prilagoditi prema broju dostupnih CPU jezgara
            overlap = 10
            image_parts_with_indices = self.split_image(num_parts, overlap)

            part_height = self.image_parallel.size[1] // num_parts

            start_time = time.time()  # Start timing

            # Obrada svakog dela paralelno
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(blur_image_part, index, part) for index, part in image_parts_with_indices]

                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            # Sortiranje delova po indeksu da bismo osigurali pravilan redosled
            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            # Spajanje obrađenih delova u jednu sliku
            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
            
            end_time = time.time()  # End timing
            duration = end_time - start_time
            # print(f"Time taken to apply flip parallel: {duration:.4f} seconds")
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")


            # Ažuriranje istorije i prikazivanje finalne slike
            self.update_history_parallel()
            self.display_image_parallel()

def get_cpu_info():
    cpu_count = psutil.cpu_count(logical=False)  # Broj fizičkih jezgara
    cpu_usage = psutil.cpu_percent(interval=1)  # Procenat opterećenja CPU-a u poslednjoj sekundi
    print(cpu_usage)
    print(cpu_count)
    return cpu_count, cpu_usage

def choose_processing_mode(cpu_count, cpu_usage, threshold=50):
    # Provera da li je opterećenje CPU-a manje od praga
    if cpu_usage < threshold:
        return "Parallel" if cpu_count > 1 else "Serial"
    else:
        return "Serial"
 
if __name__ == "__main__":
    root = tk.Tk()
    app = StartPage(root)
    num_cores, cpu_load = get_cpu_info()
    processing_mode = choose_processing_mode(num_cores, cpu_load)
    root.mainloop()