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
from tkinter import messagebox


#Funkcija za primjenu filtera boje na dijelu fotografije
def apply_color_filter_part(index, part, color):
    r, g, b = part.split()
    if color == 'red':
        r = r.point(lambda p: p * 1.5)
    elif color == 'green':
        g = g.point(lambda p: p * 1.5)
    elif color == 'blue':
        b = b.point(lambda p: p * 1.5)
    return index, Image.merge('RGB', (r, g, b))

#Funkcija za primjenu obrtanja (flipa) na dijelu fotografije
def flip_image_part(index, part):
    return index, part.transpose(Image.FLIP_LEFT_RIGHT)

#Funkcija za primjenu blura na dijelu fotografije
def blur_image_part(index, part):
    part = part.filter((ImageFilter.GaussianBlur(radius=8)))
    return index, part

#Funkcija za primjenu povećanja zasićenosti na dijelu fotografije
def process_part( index, part):
    enhancer = ImageEnhance.Color(part)
    processed_part = enhancer.enhance(1.5)
    return index, processed_part
 
#Funkcija za primjenu smanjenja zasićenosti na dijelu fotografije
def decrease_sat_part( index, part):
    enhancer = ImageEnhance.Color(part)
    processed_part = enhancer.enhance(0.5)
    return index, processed_part

#Funkcija za primjenu kompleksnog filtera u boji na dijelu fotografije
def complex_filter_part(index, part):
    # Povećanje zasićenja
    enhancer = ImageEnhance.Color(part)
    part = enhancer.enhance(1.5)

    # Primjena zamućenja
    part = part.filter(ImageFilter.BLUR)

    # Povećanje detalja
    part = part.filter(ImageFilter.DETAIL)

    # Poboljšanje ivica
    part = part.filter(ImageFilter.EDGE_ENHANCE_MORE)

    #Dodavanje dodatnih filtera za kompleksnost
    part = part.filter(ImageFilter.SHARPEN)
    part=part.filter(ImageFilter.MedianFilter(size=3))

    return index, part

#Funkcija za primjenu kompleksnog filtera BW na dijelu fotografije
def complexBW_filter_part(index, part):

    part=part.convert("L")
    # Povećanje zasićenja
    enhancer = ImageEnhance.Contrast(part)
    part = enhancer.enhance(1.5)
    
    #Postavljanje zamućenja
    part = part.filter(ImageFilter.BLUR)

    # Povećanje detalja
    part = part.filter(ImageFilter.DETAIL)

    # Poboljšanje ivica
    part = part.filter(ImageFilter.EDGE_ENHANCE_MORE)

    #Dodatni filteri za kompleksnost
    part = part.filter(ImageFilter.SHARPEN)
    part=part.filter(ImageFilter.MedianFilter(size=3))

    return index, part

#Klasa za kreiranje startne stranice
class StartPage:
    
    #Funkcija za gašenje aplikacije
    def on_closing(self):
        self.root.destroy() 

    #Funkcija za dodavanje dugmadi na početnu stranicu
    def add_buttons(self):
        # Kreiranje stila za dugmad
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

        #Kreiranje canvasa za prostor aplikacije
        self.canvas = tk.Canvas(self.root, width=self.background_image.width(), height=self.background_image.height())
        self.canvas.pack(fill="both", expand=True)
        
        # Postavljanje slike na pozadinu
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        
        # Dugme za manuelno biranje        
        btn_open_page = ttk.Button(self.root, text="Manuelno biranje", command=self.open_manual_page, style="TButton")         
        self.canvas.create_window(450, 150, anchor="w", window=btn_open_page) 

        # Dugme za automatski izbor načina obrade       
        btn_auto_process = ttk.Button(self.root, text="Automatsko biranje", command=self.auto_select_processing, style="TButton")         
        self.canvas.create_window(445, 250, anchor="w", window=btn_auto_process)

    #Funkcija za prelazak na stranicu sa automatskim izborom načina obrade
    def auto_select_processing(self):
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("Automatsko izvrsavanje")
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.image_app = ImageUploaderApp(self.main_window, processing_mode) 
        self.root.withdraw()
        
    #Funkcija za prelazak na stranicu sa manuelnim izborom načina obrade
    def open_manual_page(self):
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("Manuelno izvrsavanje")
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.image_app = ImageUploaderApp(self.main_window, "Manual") 
        self.root.withdraw()
        
    #Funkcija za dodavanje labela na početnu stranicu
    def add_artify_text(self):
        # Kreiranje fonta
        custom_font = font.Font(family="Lucida Handwriting", size=38, weight="bold")

        self.canvas.create_text(330, 200, text="Artify", font=custom_font, fill="white", anchor="center")
        
    #Funkcija __init - konstruktor za kreiranje početne stranice, objekta klase StartPage
    def __init__(self, root):
        self.root = root
        self.root.configure(bg='#F1E5D1')
        self.root.resizable(False, False)

        icon = PhotoImage(file='icon.png')
        self.root.iconphoto(True, icon)
        window_width = 600
        window_height = 400

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        position_x = int(screen_width/2 - window_width/2)
        position_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        self.background_image = tk.PhotoImage(file="pozNovo.png")

        background_label = tk.Label(self.root, image=self.background_image)
        background_label.image = self.background_image  # Ovo je važno začuvanje reference na sliku
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.root.title(f"Artify")
        self.add_buttons()
        self.add_artify_text()
        
#Klasa za kreiranje stranice za uređivanje slike
class ImageUploaderApp:
    
    #Funkcija __init - konstruktor za kreiranje stranice za uređivanje slike, objekta klase ImageUploaderApp
    def __init__(self, root, param):
        self.pool = multiprocessing.Pool(processes=psutil.cpu_count(logical=False))
        self.root = root
        self.root.configure(bg='#FFF8DC')  
        self.root.resizable(False, False)
        space=(" ")*220

        self.root.title(f"{space}Image Editor")
        icon= PhotoImage(file='icon.png')
        self.root.iconphoto(True, icon)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
 
        image_width = screen_width // 3
        image_height = screen_height // 2

        
        window_width = 1500
        window_height = 740
        position_x = int(screen_width/2 - window_width/2-8)
        position_y = int(screen_height/2 - window_height/2-40)

        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        #Kreiranje Frame widgeta za učitavavnje slike i obradu u serijskom izvršavanju
        self.left_frame = tk.Frame(root, bg='#FFF8DC')
        self.left_frame.pack(side='left', fill='both', expand=True)
        self.left_frame.pack_propagate(0) 
        label_serial = tk.Label(self.left_frame, text="Serijsko izvršavanje", bg='#FFF8DC', font=("Helvetica", 20), fg='#640D6B')
        label_serial.pack(side='top', pady=(10, 0)) 
        self.label_text=tk.Label(self.left_frame, text="", bg='#FFF8DC', font=("Helvetica", 14), fg='#640D6B')
        self.label_text.pack(side='bottom', pady=(0, 0))

        #Kreiranje Frame widgeta za učitavavnje slike i obradu u paralelnom izvršavanju
        self.right_frame = tk.Frame(root, bg='#FFF8DC')
        self.right_frame.pack(side='right', fill='both', expand=True)
        self.right_frame.pack_propagate(0) 
        label_parallel = tk.Label(self.right_frame, text="Paralelno izvršavanje", bg='#FFF8DC', font=("Helvetica", 20), fg='#B51B75')
        label_parallel.pack(side='top', pady=(10, 0))  # Postavljanje natpisa na vrh i centriranje horizontalno
        self.label_text_par=tk.Label(self.right_frame, text="", bg='#FFF8DC', font=("Helvetica", 14), fg='#640D6B')
        self.label_text_par.pack(side='bottom', pady=(0, 0))
 
        # Kreiranje stila za separator
        style = ttk.Style()
        style.configure("CustomSeparator.TSeparator", background='#EEA5A6', borderwidth=3, relief="sunken")
        separator = ttk.Separator(root, orient='vertical', style="CustomSeparator.TSeparator")
        separator.pack(side='left', fill='y', padx=10)
       
 
        # Funkcija za kreiranje okvira s Canvasom i teksturom slike
        def create_image_frame(parent_frame):
            image_frame = tk.Frame(parent_frame, bg='#EEA5A6', highlightbackground='#EEA5A6', highlightthickness=4)
            image_frame.pack(side='left', fill='none', expand=True, padx=10, pady=5)

            image_canvas = tk.Canvas(image_frame, width=image_width, height=image_height)
            image_canvas.pack(expand=True, fill='both')

            image1 = Image.open("slika1.png")
            photo1 = ImageTk.PhotoImage(image1)
            
            image_canvas.image = photo1
            image_canvas.create_image(0, 0, anchor=tk.NW, image=photo1)
            image_canvas.create_text(image_width // 2, image_height // 2, text="Fotografija će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 20))
 
            return image_canvas
 
        # Kreiranje lijevog okvira za sliku i dugmad (serijsko izvršavanje)
        self.image_canvas = create_image_frame(self.left_frame)

        button_frame_canvas = tk.Canvas(self.left_frame, bg='#FFF8DC', highlightthickness=0)
        button_frame_canvas.pack(side='right', fill='y', expand=False) 
        button_frame = tk.Frame(button_frame_canvas, bg='#FFF8DC')
        button_frame.pack(anchor='ne')   
        button_frame.bind("<Configure>", lambda e: button_frame_canvas.configure(scrollregion=button_frame_canvas.bbox("all")))
 
        # Kreiranje dugmadi i grupisanje po funkcionalnosti
        style = ttk.Style()
        style.configure("Main.TButton", font=("Helvetica", 10), padding=5, background='#D74B76',foreground='#EF9595')
        style.map("Main.TButton", background=[('active', '#EF9595')])
        style.map("Main.TButton", foreground=[('active', "#D74B76")])

        # Učitavanje ikonice za Undo, Redo, Cut, Flip, Rotate
        undo_icon = Image.open("undo.png") 
        undo_icon = undo_icon.resize((20, 20), Image.LANCZOS)
        undo_icon = ImageTk.PhotoImage(undo_icon)

        redo_icon = Image.open("redo.png") 
        redo_icon = redo_icon.resize((20, 20), Image.LANCZOS) 
        redo_icon = ImageTk.PhotoImage(redo_icon)

        cut_icon = Image.open("cut.png") 
        cut_icon = cut_icon.resize((20, 20), Image.LANCZOS) 
        cut_icon = ImageTk.PhotoImage(cut_icon)

        flip_icon = Image.open("flip.png")  
        flip_icon = flip_icon.resize((20, 20), Image.LANCZOS) 
        flip_icon = ImageTk.PhotoImage(flip_icon)

        rotate_icon = Image.open("rotate.png")  
        rotate_icon = rotate_icon.resize((20, 20), Image.LANCZOS)  
        rotate_icon = ImageTk.PhotoImage(rotate_icon)
 
        buttons_left = [
            ("Učitaj fotografiju", self.upload_image),
            ("Poništi filtere", self.reset_image),
            ("Sačuvaj fotografiju", self.save_image),
            ("Zatvori fotografiju", self.close_image),
            ("Povećaj zasićenje", self.increase_saturation),
            ("Smanji zasićenje", self.reduce_saturation),
            ("Zamućenje", self.blurr),           
        ]
        
        style1 = ttk.Style()
        style1.configure("Complex.TButton", font=("Helvetica", 10), padding=5, background='#541be5',foreground='#674ea7')
        style1.map("Complex.TButton", background=[('active', '#674ea7')])
        style1.map("Complex.TButton", foreground=[('active', "#541be5")])


        buttons_complex_left= [
            ("Kompleksni filter-boje", self.apply_complex_filter_serial),
            ("Kompleksni filter-BW", self.apply_complexBW_filter_serial)
        ]
 
        for text, command in buttons_left:
            button = ttk.Button(button_frame, text=text, command=command, width=18, style="Main.TButton")
            button.pack(pady=5)
        for text, command in buttons_complex_left:
            button = ttk.Button(button_frame, text=text, command=command, width=18, style="Complex.TButton")
            button.pack(pady=5)

        # Kreiranje okvira za cut/rotate
        cutrotate_frame_left = tk.Frame(button_frame, bg='#FFF8DC')
        cutrotate_frame_left.pack(pady=10)

        cut_button = ttk.Button(cutrotate_frame_left, image=cut_icon, command=self.start_crop)
        cut_button.image = cut_icon 
        cut_button.pack(side='left', padx=5, pady=10)

        rotate_button = ttk.Button(cutrotate_frame_left, image=rotate_icon, command=self.rotate_image)
        rotate_button.image = rotate_icon 
        rotate_button.pack(side='left', padx=5, pady=10)

        flip_button = ttk.Button(cutrotate_frame_left, image=flip_icon, command=self.flip)
        flip_button.image = flip_icon 
        flip_button.pack(side='left', padx=5, pady=10)

        #Funkcije za promjenu izgleda dugmadi u zavisnosti od toga da li su dugmad u fokusu ili ne
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

        # Kreiranje okvira za boje (serijsko izvršavanje)
        color_frame_left = tk.Frame(button_frame, bg='#FFF8DC')
        color_frame_left.pack(pady=10)
 
        colors_left = [
            ("Plavi", lambda: self.apply_color_filter('blue'), '#034b81', '#99cff8'),
            ("Crveni", lambda: self.apply_color_filter('red'), '#ac1004','#f88b83'),
            ("Zeleni", lambda: self.apply_color_filter('green'), '#38761d', '#74fb3a')
        ]

        for text, command, color, fgText in colors_left:
            button = tk.Button(color_frame_left, text=text, command=command, width=7, bg=color,fg=fgText, bd=1)
            button.pack(side='left', padx=5)
            
            if color == '#034b81':
                button.bind('<Enter>', on_enter_blue)
                button.bind('<Leave>', on_leave_blue)
            elif color == '#ac1004':
                button.bind('<Enter>', on_enter_red)
                button.bind('<Leave>', on_leave_red)
            elif color == '#38761d':
                button.bind('<Enter>', on_enter_green)
                button.bind('<Leave>', on_leave_green)


        # Kreiranje okvira za undo/redo 
        undoredo_frame_left = tk.Frame(button_frame, bg='#FFF8DC')
        undoredo_frame_left.pack(pady=10)
 

        undo_button = ttk.Button(undoredo_frame_left, image=undo_icon, command=self.undo)
        undo_button.image = undo_icon 
        undo_button.pack(side='left', padx=5, pady=10)

        redo_button = ttk.Button(undoredo_frame_left, image=redo_icon, command=self.redo)
        redo_button.image = redo_icon  
        redo_button.pack(side='left', padx=5, pady=10)
 
 
        # Kreiranje desnog okvira za sliku i dufgmad (paralelno izvršavanje)
        self.image_canvas_parallel = create_image_frame(self.right_frame)
 
        button_frame_canvas_parallel = tk.Canvas(self.right_frame, bg='#FFF8DC', highlightthickness=0)
        button_frame_canvas_parallel.pack(side='right', fill='y', expand=False)
 
 
        button_frame_parallel = tk.Frame(button_frame_canvas_parallel, bg='#FFF8DC')
        button_frame_parallel.pack(anchor='ne')  
 
        button_frame_parallel.bind("<Configure>", lambda e: button_frame_canvas_parallel.configure(scrollregion=button_frame_canvas_parallel.bbox("all")))
 
        # Kreiranje dugmadi i grupisanje po funkcionalnosti
        buttons_right = [
            ("Učitaj fotografiju", self.upload_image_parallel),
            ("Poništi filtere", self.reset_image_parallel),
            ("Sačuvaj fotografiju", self.save_image_parallel),
            ("Zatvori fotografiju", self.close_image_parallel),
            ("Povećaj zasićenje", lambda: self.increase_saturation_parallel(psutil.cpu_count(logical=False))),
            ("Smanji zasićenje", lambda: self.reduce_saturation_parallel(psutil.cpu_count(logical=False))),
            ("Zamućenje", self.blurr_parallel),
        ]

        style1 = ttk.Style()
        style1.configure("Complex.TButton", font=("Helvetica", 10), padding=5, background='#541be5',foreground='#674ea7')
        style1.map("Complex.TButton", background=[('active', '#674ea7')])
        style1.map("Complex.TButton", foreground=[('active', "#541be5")])


        buttons_complex_right= [
            ("Kompleksni filter-boje", lambda:self.apply_complex_filter_parallel(psutil.cpu_count(logical=False))),
            ("Kompleksni filter-BW", lambda:self.apply_complexBW_filter_parallel(psutil.cpu_count(logical=False))),
        ]
 
        for text, command in buttons_right:
            button = ttk.Button(button_frame_parallel, text=text, command=command, width=18, style="Main.TButton")
            button.pack(pady=5)

        for text, command in buttons_complex_right:
            button = ttk.Button(button_frame_parallel, text=text, command=command, width=18, style="Complex.TButton")
            button.pack(pady=5)

        
         # Kreiranje okvira za cut/rotate
        cutrotate_frame_right = tk.Frame(button_frame_parallel, bg='#FFF8DC')
        cutrotate_frame_right.pack(pady=10)

        cut_button_parallel = ttk.Button(cutrotate_frame_right, image=cut_icon, command=self.start_crop_parallel)
        cut_button_parallel.image = cut_icon 
        cut_button_parallel.pack(side='left', padx=5, pady=10)

        rotate_button_parallel = ttk.Button(cutrotate_frame_right, image=rotate_icon, command=self.rotate_image_parallel)
        rotate_button_parallel.image = rotate_icon  
        rotate_button_parallel.pack(side='left', padx=5, pady=10)

        flip_button_parallel = ttk.Button(cutrotate_frame_right, image=flip_icon, command=self.flip_parallel)
        flip_button_parallel.image = flip_icon  
        flip_button_parallel.pack(side='left', padx=5, pady=10)

         # Kreiranje okvira za boje
        color_frame_right = tk.Frame(button_frame_parallel, bg='#FFF8DC')
        color_frame_right.pack(pady=10)
 
        colors_right = [
             ("Plavi", lambda: self.apply_color_filter_parallel('blue'), '#034b81', '#99cff8'),
            ("Crveni", lambda: self.apply_color_filter_parallel('red'), '#ac1004','#f88b83'),
            ("Zeleni", lambda: self.apply_color_filter_parallel('green'), '#38761d', '#74fb3a')
        ]
 
        for text, command, color, fgText in colors_right:
            button = tk.Button(color_frame_right, text=text, command=command, width=7, bg=color,fg=fgText, bd=1)
            button.pack(side='left', padx=5)
            
            if color == '#034b81':
                button.bind('<Enter>', on_enter_blue)
                button.bind('<Leave>', on_leave_blue)
            elif color == '#ac1004':
                button.bind('<Enter>', on_enter_red)
                button.bind('<Leave>', on_leave_red)
            elif color == '#38761d':
                button.bind('<Enter>', on_enter_green)
                button.bind('<Leave>', on_leave_green)


         # Kreiranje okvira za undo/redo 
        undoredo_frame_right = tk.Frame(button_frame_parallel, bg='#FFF8DC')
        undoredo_frame_right.pack(pady=10)


        undo_button_parallel = ttk.Button(undoredo_frame_right, image=undo_icon, command=self.undo_parallel)
        undo_button_parallel.image = undo_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        undo_button_parallel.pack(side='left', padx=5, pady=10)

        redo_button_parallel = ttk.Button(undoredo_frame_right, image=redo_icon, command=self.redo_parallel)
        redo_button_parallel.image = redo_icon  # Očuvaj referencu na sliku da se spriječi brisanje iz memorije
        redo_button_parallel.pack(side='left', padx=5, pady=10)
 
        
        # Inicijalizacija slike i istorije za serijsko izvršavanje
        self.image = None
        self.image_history = []
        self.history_index = -1
 
        # Inicijalizacija slike i istorije za paralelno izvršavanje
        self.image_parallel = None
        self.image_history_parallel = []
        self.history_index_parallel = -1

        if(param=="Parallel"):
            self.left_frame.destroy()
            separator.destroy()
        elif(param=="Serial"):
            self.right_frame.destroy()
            separator.destroy()
            
    #Funkcija za učitavanje slike u canvas za serijsko izvršavanje
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            self.image = Image.open(file_path)
            original_width=self.image.width
            original_height=self.image.height
            self.image_history = [self.image.copy()]
            imgwidth=self.image.width
            imgheight=self.image.height

            self.history_index = 0
            self.display_image()
            self.label_text.config(text=f"Dimenzije slike {imgwidth}x{imgheight}.")
            if(original_height>=1800 and original_width>=1800):
                messagebox.showinfo("Obavještenje", "Preporučuje se paralelna obrada fotografije!")

                

    #Funkcija za učitavanje slike u canvas za paralelno izvršavanje
    def upload_image_parallel(self): 
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path: 
            self.image_parallel = Image.open(file_path) 
            original_width=self.image_parallel.width
            original_height=self.image_parallel.height
            self.image_history_parallel = [self.image_parallel.copy()] 

            imgwidth=self.image_parallel.width
            imgheight=self.image_parallel.height

            self.history_index_parallel = 0 
            self.display_image_parallel() 
            self.label_text_par.config(text=f"Dimenzije slike {imgwidth}x{imgheight}.")
            
            if(original_height<=1800 and original_width<=1800):
                messagebox.showinfo("Obavještenje", "Preporučuje se serijska obrada fotografije!")

    #Funkcija za prikazivanje slike u canvasu za serijsko izvršavanje
    def display_image(self):
        if self.image:
            img=self.image
            self.image_canvas.delete("all")
            image_width=self.root.winfo_width()//3
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
 
            image_width, image_height =img.size
            x_offset = (canvas_width - image_width) / 2
            y_offset = (canvas_height - image_height) / 2
            self.photo = ImageTk.PhotoImage(img)
 
            self.image_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)
 
    #Funkcija za uklanjanje slike iz canvasa za serijsko izvršavanje
    def close_image(self):
        if self.image:
            self.image_canvas.delete("all")    

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
 
            image_width = screen_width // 3
            image_height = screen_height // 2

            self.image_canvas.config(width=image_width, height=image_height)

            self.image_canvas.pack(expand=True, fill='both')

            image1 = Image.open("slika1.png")
            photo1 = ImageTk.PhotoImage(image1)
            
            self.image_canvas.image = photo1
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=photo1)
            self.image_canvas.create_text(image_width // 2, image_height // 2, text="Fotografija će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 20))
            self.label_text.config(text="Fotografija uklonjena")
            self.history_index=0
            self.image_history = [None]

    #Funkcija za uklanjanje slike iz canvasa za paralelno izvršavanje
    def close_image_parallel(self):
        if self.image_parallel:
            self.image_canvas_parallel.delete("all")    
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
 
            image_width = screen_width // 3
            image_height = screen_height // 2

            self.image_canvas_parallel.config(width=image_width, height=image_height)
            self.image_canvas_parallel.pack(expand=True, fill='both')

            image1 = Image.open("slika1.png")
            photo1 = ImageTk.PhotoImage(image1)
            
            self.image_canvas_parallel.image = photo1
            self.image_canvas_parallel.create_image(0, 0, anchor=tk.NW, image=photo1)
            self.image_canvas_parallel.create_text(image_width // 2, image_height // 2, text="Fotografija će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 20))
            self.label_text_par.config(text="Fotografija uklonjena")
            self.history_index_parallel=0
            self.image_history_parallel = [None]


    #Funkcija za prikazivanje slike u canvasu za paralelno izvršavanje
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
 
            image_width, image_height =img.size
            x_offset = (canvas_width - image_width) / 2
            y_offset = (canvas_height - image_height) / 2
            self.photo_parallel = ImageTk.PhotoImage(img)
 
            self.image_canvas_parallel.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo_parallel)
            
    #Funkcija za resetovanje filtera sa slike za serijsko izvršavanje
    def reset_image(self):
        if self.image_history:
            self.image = self.image_history[0]
            self.history_index = 0
            self.display_image()
            if self.image:
                self.label_text.config(text="Filteri resetovani")

    #Funkcija za resetovanje filtera sa slike za paralelno izvršavanje
    def reset_image_parallel(self): 
        if self.image_history_parallel: 
            self.image_parallel = self.image_history_parallel[0] 
            self.history_index_parallel = 0 
            self.display_image_parallel() 
            if self.image_parallel:
                self.label_text_par.config(text="Filteri resetovani")

    #Funkcija za čuvanje fotografije za serijsko izvršavanje
    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("BMP files", "*.bmp"),
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ]
    )
            if file_path:
                self.image.save(file_path)
                self.label_text.config(text=f"Fotografija {file_path} je sačuvana")
                messagebox.showinfo("Obavještenje", f"Fotografija je sačuvana na lokaciju {file_path}")
 
     #Funkcija za čuvanje fotografije za paralelno izvršavanje
    def save_image_parallel(self): 
        if self.image_parallel: 
            file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("BMP files", "*.bmp"),
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ]
    )
            if file_path: 
                self.image_parallel.save(file_path) 
                self.label_text_par.config(text=f"Fotografija {file_path} je sačuvana")
                messagebox.showinfo("Obavještenje", f"Fotografija je sačuvana na lokaciju {file_path}")

    #Funkcija za povećanje zasićenosti fotografije za serijsko izvršavanje
    def increase_saturation(self):
        if self.image:
            start_time = time.time()  
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(1.5)
            end_time = time.time()  
            duration = end_time - start_time
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            self.update_history()
            self.display_image()
 
    #Funkcija za povećanje zasićenosti fotografije za paralelno izvršavanje
    def increase_saturation_parallel(self, num_parts):
        if not self.image_parallel:
            return

        overlap = 10  
        image_parts_with_indices = self.split_image(num_parts, overlap)

        part_height = self.image_parallel.size[1] // num_parts

        start_time = time.time() 
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_part, index, part) for index, part in image_parts_with_indices]

            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())

        processed_parts.sort(key=lambda x: x[0])
        processed_parts = [part for index, part in processed_parts]

        self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)

        end_time = time.time()  
        duration = end_time - start_time
        self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
        self.update_history_parallel()
        self.display_image_parallel()

    #Funkcija za dijeljenje fotografije za paralelno izvršavanje
    def split_image(self, num_parts, overlap=10):
        width, height = self.image_parallel.size
        part_height = height // num_parts
        image_parts_with_indices = []

        for i in range(num_parts):
            upper = max(0, i * part_height - overlap)
            lower = min(height, (i + 1) * part_height + overlap)
            part = self.image_parallel.crop((0, upper, width, lower))
            image_parts_with_indices.append((i, part))

        return image_parts_with_indices
    
    #Funkcija za spajanje dijelova fotografije za paralelno izvršavanje
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

        return merged_image
 
    #Funkcija za smanjenje zasićenosti fotografije za serijsko izvršavanje
    def reduce_saturation(self):
        if self.image:
            start_time = time.time()  
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(0.5)
            end_time = time.time()  
            duration = end_time - start_time
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            self.update_history()
            self.display_image()
 
    #Funkcija za smanjenje zasićenosti fotografije za paralelno izvršavanje
    def reduce_saturation_parallel(self, num_parts): # ADDED
        if self.image_parallel: 

            overlap = 10  
            image_parts_with_indices = self.split_image(num_parts, overlap)

            part_height = self.image_parallel.size[1] // num_parts

            start_time = time.time()
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(decrease_sat_part, index, part) for index, part in image_parts_with_indices]

                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)

            end_time = time.time() 
            duration = end_time - start_time
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            self.update_history_parallel()
            self.display_image_parallel()
        else:
            return
        
    #Funkcija za primjenu kompleksnog filtera u boji na fotografiju za serijsko izvršavanje
    def apply_complex_filter_serial(self):
        if not self.image:
            return
        start_time = time.time()
        enhancer = ImageEnhance.Color(self.image)
        self.image = enhancer.enhance(1.5)
        self.image = self.image.filter(ImageFilter.BLUR)
        self.image = self.image.filter(ImageFilter.DETAIL)
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        self.image = self.image.filter(ImageFilter.SHARPEN)
        self.image=self.image.filter(ImageFilter.MedianFilter(size=3))

        end_time = time.time()
        duration = end_time - start_time
        self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
        self.update_history()
        self.display_image()
        
    #Funkcija za primjenu kompleksnog filtera BW na fotografiju za serijsko izvršavanje
    def apply_complexBW_filter_serial(self):
        if not self.image:
            return
        start_time = time.time()

        self.image = self.image.convert("L")
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(1.5)
        self.image = self.image.filter(ImageFilter.BLUR)
        self.image = self.image.filter(ImageFilter.DETAIL)
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        self.image = self.image.filter(ImageFilter.SHARPEN)
        self.image = self.image.filter(ImageFilter.MedianFilter(size=3))

        end_time = time.time()
        duration = end_time - start_time
        self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
        self.update_history()
        self.display_image()
        
    #Funkcija za primjenu kompleksnog filtera u boji na fotografiju za paralelno izvršavanje
    def apply_complex_filter_parallel(self, num_parts):
        if not self.image_parallel:
            return
        overlap = 10  
        image_parts_with_indices = self.split_image(num_parts, overlap)

        part_height = self.image_parallel.size[1] // num_parts

        start_time = time.time()
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(complex_filter_part, index, part) for index, part in image_parts_with_indices]

            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())

        processed_parts.sort(key=lambda x: x[0])
        processed_parts = [part for index, part in processed_parts]

        self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
        
        end_time = time.time() 
        duration = end_time - start_time
        self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")

        self.update_history_parallel()
        self.display_image_parallel()
        
    #Funkcija za primjenu kompleksnog filtera BW na fotografiju za paralelno izvršavanje
    def apply_complexBW_filter_parallel(self, num_parts):
        if not self.image_parallel:
            return

        overlap = 10 
        image_parts_with_indices = self.split_image(num_parts, overlap)

        part_height = self.image_parallel.size[1] // num_parts

        start_time = time.time()
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(complexBW_filter_part, index, part) for index, part in image_parts_with_indices]

            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())

        processed_parts.sort(key=lambda x: x[0])
        processed_parts = [part for index, part in processed_parts]

        self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
        
        end_time = time.time() 
        duration = end_time - start_time
        self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")

        self.update_history_parallel()
        self.display_image_parallel()

    #Funkcija za primjenu filtera boje na fotografiju za serijsko izvršavanje
    def apply_color_filter(self, color):
        if self.image:

            start_time = time.time()

            r, g, b = self.image.split()
            if color == 'red':
                r = r.point(lambda p: p * 1.5)
            elif color == 'green':
                g = g.point(lambda p: p * 1.5)
            elif color == 'blue':
                b = b.point(lambda p: p * 1.5)
            self.image = Image.merge('RGB', (r, g, b))


            end_time = time.time() 
            duration = end_time - start_time
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            self.update_history()
            self.display_image()
            
    #Funkcija za primjenu filtera boje na fotografiju za paralelno izvršavanje
    def apply_color_filter_parallel(self, color):
        if self.image_parallel:
            num_parts = psutil.cpu_count(logical=False)
            overlap = 10
            image_parts_with_indices = self.split_image(num_parts, overlap)

            part_height = self.image_parallel.size[1] // num_parts

            start_time = time.time()

            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(apply_color_filter_part, index, part, color) for index, part in image_parts_with_indices]

                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
            
            end_time = time.time()
            duration = end_time - start_time
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            
            self.update_history_parallel()
            self.display_image_parallel()
 
 
    #Funkcija za primjenu rotacije na fotografiju za serijsko izvršavanje
    def rotate_image(self):
        if self.image:
            img=self.image
            img = img.transpose(Image.ROTATE_90)
            self.image=img
            self.update_history() 
            self.display_image()
            self.label_text.config(text="Fotografija rotirana za 90 stepeni")
            
   #Funkcija za primjenu rotacije na fotografiju za paralelno izvršavanje
    def rotate_image_parallel(self): 

         if self.image_parallel:
            img=self.image_parallel
            img = img.transpose(Image.ROTATE_90)
            self.image_parallel=img
            self.update_history_parallel() 
            self.display_image_parallel()
            self.label_text_par.config(text="Fotografija rotirana za 90 stepeni")
    
    #Funkcije za isijecanje fotografije za serijsko i paralelno izvršavanje, a obuhvataju pritisak, zadržavanje i otpuštanje pritiska na miš
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
    
    #Funkcija za isijecanje fotografije za serijsko izvršavanje
    def crop_image(self):
        if self.image:
            start_time = time.time() 

            original_width, original_height = self.image.size
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
           
            scale_x = original_width / canvas_width
            scale_y = original_height / canvas_height
           
            crop_start_x = int(self.crop_start_x * scale_x)
            crop_start_y = int(self.crop_start_y * scale_y)
            crop_end_x = int(self.crop_end_x * scale_x)
            crop_end_y = int(self.crop_end_y * scale_y)
           
            cropped_image = self.image.crop((crop_start_x, crop_start_y, crop_end_x, crop_end_y))
            self.image = cropped_image

            width=self.image.width
            height=self.image.height

            end_time = time.time() 
            duration = end_time - start_time

            self.label_text.config(text=f"Dimenzija isječene slike {width}x{height}")
            
            self.update_history()
            self.display_image()
            
    #Funkcija za isijecanje fotografije za paralelno izvršavanje
    def crop_image_parallel(self):
        if self.image_parallel:
            start_time = time.time() 

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

            end_time = time.time()  
            duration = end_time - start_time

            self.label_text_par.config(text=f"Dimenzija isječene slike {width}x{height}")

            self.update_history_parallel()
            self.display_image_parallel()
            
    #Funkcija za poništavanje prethodnog filtera sa fotografije za serijsko izvršavanje
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.image_history[self.history_index]
            self.display_image()
            self.label_text.config(text="Undo akcija izvršena")
            
     #Funkcija za poništavanje prethodnog filtera sa fotografije za paralelno izvršavanje
    def undo_parallel(self): 
        if self.history_index_parallel > 0: 
            self.history_index_parallel -= 1 
            self.image_parallel = self.image_history_parallel[self.history_index_parallel] 
            self.display_image_parallel() 
            self.label_text_par.config(text="Undo akcija izvršena")
    
    #Funkcija za vraćanje prethodno poništenog filtera sa fotografije za serijsko izvršavanje
    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.image = self.image_history[self.history_index]
            self.display_image()
            self.label_text.config(text="Redo akcija izvršena")
            
    #Funkcija za vraćanje prethodno poništenog filtera sa fotografije za paralelno izvršavanje
    def redo_parallel(self): 
        if self.history_index_parallel < len(self.image_history_parallel) - 1: 
            self.history_index_parallel += 1 
            self.image_parallel = self.image_history_parallel[self.history_index_parallel] 
            self.display_image_parallel() 
            self.label_text.config(text="Redo akcija izvršena")


    #Funkcija za pamćenje koraka pri obradi fotografije za serijsku obradu
    def update_history(self):
        self.image_history = self.image_history[:self.history_index + 1]
        self.image_history.append(self.image.copy())
        self.history_index += 1
 
    #Funkcija za pamćenje koraka pri obradi fotografije za paralelnu obradu
    def update_history_parallel(self): 
        self.image_history_parallel = self.image_history_parallel[:self.history_index_parallel + 1] 
        self.image_history_parallel.append(self.image_parallel.copy()) 
        self.history_index_parallel += 1 
 
    #Funkcija za obrtanje fotografije (slika u ogledalu) za serijsku obradu
    def flip(self):
        if(self.image):
            start_time = time.time()  
            self.image = self.image.transpose((Image.FLIP_LEFT_RIGHT))            
            end_time = time.time()  
            duration = end_time - start_time
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            self.update_history()
            self.display_image()
 
    #Funkcija za obrtanje fotografije (slika u ogledalu) za paralelnu obradu
    def flip_parallel(self):
        if self.image_parallel:
            num_parts = psutil.cpu_count(logical=False)  
            overlap = 10
            image_parts_with_indices = self.split_image(num_parts, overlap)
            part_height = self.image_parallel.size[1] // num_parts
            start_time = time.time()  
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(flip_image_part, index, part) for index, part in image_parts_with_indices]
                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())

            # Sortiranje dijelova po indeksu da bismo osigurali pravilan redoslijed
            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)
            
            end_time = time.time() 
            duration = end_time - start_time
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} sekundi")
            self.update_history_parallel()
            self.display_image_parallel()

    #Funkcija za zamućenje fotografije za serijsku obradu
    def blurr(self):
        if(self.image):
            start_time = time.time()  
            self.image = self.image.filter((ImageFilter.GaussianBlur(radius=8)))
            end_time = time.time()  
            duration = end_time - start_time
            self.update_history()
            self.display_image()
            self.label_text.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
 
    #Funkcija za zamućenje fotografije za paralelnu obradu
    def blurr_parallel(self):
        if self.image_parallel:
            num_parts = psutil.cpu_count(logical=False) 
            overlap = 10
            image_parts_with_indices = self.split_image(num_parts, overlap)
            part_height = self.image_parallel.size[1] // num_parts
            start_time = time.time() 
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(blur_image_part, index, part) for index, part in image_parts_with_indices]
                processed_parts = []
                for future in as_completed(futures):
                    processed_parts.append(future.result())
            processed_parts.sort(key=lambda x: x[0])
            processed_parts = [part for index, part in processed_parts]

            self.image_parallel = self.merge_image_parts(processed_parts, part_height, overlap)            
            end_time = time.time() 
            duration = end_time - start_time
            self.label_text_par.config(text=f"Vrijeme izvršavanja: {duration:.4f} seconds")
            self.update_history_parallel()
            self.display_image_parallel()

#Funkcija za dobijanje podataka o korisničkom računaru
def get_cpu_info():
    #Dobijanje broja fizičkih jezgara
    cpu_count = psutil.cpu_count(logical=False) 
    #Dobijanje procenta opterećenja procesora 
    cpu_usage = psutil.cpu_percent(interval=1) 
    return cpu_count, cpu_usage

#Funkcija za određivanje načina obrade fotografije
def choose_processing_mode(cpu_count, cpu_usage, threshold=50):
    #Provjera da li je opterećenje CPU-a manje od zadatog praga
    if cpu_usage < threshold:
        return "Parallel" if cpu_count > 1 else "Serial"
    else:
        return "Serial"

#Funkcija za pokretanje aplikacije
if __name__ == "__main__":
    #Inicijalizacija glavnog prozora aplikacije
    root = tk.Tk()
    app = StartPage(root)
    num_cores, cpu_load = get_cpu_info()
    processing_mode = choose_processing_mode(num_cores, cpu_load)

    #Pokretanje Tkinter petlje događaja
    root.mainloop()