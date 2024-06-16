import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import multiprocessing
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class ImageUploaderApp:
    def __init__(self, root):
        # num_cores = os.cpu_count()
        # print(f"Number of logical CPUs: {num_cores}")
        # num_processes = multiprocessing.cpu_count()
        # self.pool = multiprocessing.Pool(4)
        self.pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

        print(self.pool)
        self.root = root
        self.root.state('zoomed')  # Maksimiziraj prozor da pokrije ekran osim trake sa zadacima
        self.root.configure(bg='#FFF8DC')  # Postavi boju pozadine na lila
        
        space=(" ")*215
        
        self.root.title(f"{space}Image Editor")
        # Dobavi širinu i visinu ekrana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Izračunaj dimenzije za sliku tako da zauzima jednu trećinu visine ekrana
        image_width = screen_width // 3
        image_height = screen_height // 2

        # Kreiraj okvir za lijevu stranu (serijsko izvršavanje)
        left_frame = tk.Frame(root, bg='#FFF8DC')
        left_frame.pack(side='left', fill='both', expand=True)

        label_serial = tk.Label(left_frame, text="Serijsko izvršavanje", bg='#FFF8DC', font=("Helvetica", 20), fg='#640D6B')
        label_serial.pack(side='top', pady=(10, 0))  # Postavljanje natpisa na vrh i centriranje horizontalno

        # Kreiraj okvir za desnu stranu (paralelno izvršavanje)
        right_frame = tk.Frame(root, bg='#FFF8DC')
        right_frame.pack(side='right', fill='both', expand=True)

        # Kreiranje natpisa "Paralelno izvršavanje"
        label_parallel = tk.Label(right_frame, text="Paralelno izvršavanje", bg='#FFF8DC', font=("Helvetica", 20), fg='#B51B75')
        label_parallel.pack(side='top', pady=(10, 0))  # Postavljanje natpisa na vrh i centriranje horizontalno


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

            image_canvas = tk.Canvas(image_frame, width=image_width, height=image_height, bg='#E0AED0')
            image_canvas.pack(expand=True, fill='both')

            image_canvas.create_text(image_width // 2, image_height // 2, text="Slika će se prikazati ovdje", fill='#4B0082', font=("Helvetica", 16))

            return image_canvas

        # Kreiraj lijevi okvir za sliku i gumbe (serijsko izvršavanje)
        self.image_canvas = create_image_frame(left_frame)

        # Kreiraj okvir za gumbe s ljeve strane uz scrollbar
        # button_frame_canvas = tk.Canvas(left_frame, bg='#E6E6FA')
        # button_frame_canvas.pack(side='right', fill='y', expand=False)

        # scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=button_frame_canvas.yview)
        # scrollbar.pack(side="right", fill="y")

        # button_frame = tk.Frame(button_frame_canvas, bg='#E6E6FA')

        # button_frame_canvas.create_window((0, 0), window=button_frame, anchor='nw')
        # button_frame_canvas.configure(yscrollcommand=scrollbar.set)
        button_frame_canvas = tk.Canvas(left_frame, bg='#FFF8DC', highlightthickness=0)
        button_frame_canvas.pack(side='right', fill='y', expand=False)

        #scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=button_frame_canvas.yview)
        #scrollbar.pack(side="right", fill="y")

        button_frame = tk.Frame(button_frame_canvas, bg='#FFF8DC')
        button_frame.pack(anchor='ne')  # Postavljamo anchor na 'ne' kako bismo postavili button_frame u gornji desni ugao button_frame_canvas
        

        #button_frame_canvas.configure(yscrollcommand=scrollbar.set)

        button_frame.bind("<Configure>", lambda e: button_frame_canvas.configure(scrollregion=button_frame_canvas.bbox("all")))

        # Kreiraj gumbe i grupiraj ih po funkcionalnosti
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10), padding=5, background='#D74B76',foreground='#EF9595')
        style.map("TButton", background=[('active', '#EF9595')])
        style.map("TButton", foreground=[('active', "#D74B76")])

        buttons_left = [
            ("Upload Image", self.upload_image), 
            ("Reset", self.reset_image), 
            ("Save Image", self.save_image),
            ("Increase Saturation", self.increase_saturation),
            ("Reduce Saturation", self.reduce_saturation),
            ("Blue", lambda: self.apply_color_filter('blue')),
            ("Red", lambda: self.apply_color_filter('red')),
            ("Green", lambda: self.apply_color_filter('green')),
            ("Rotate", self.rotate_image),
            ("Crop", self.start_crop),
            ("Flip", self.flip),
            ("Blur", self.blurr),
            ("Undo", self.undo),
            ("Redo", self.redo)
        ]

        for text, command in buttons_left:
            button = ttk.Button(button_frame, text=text, command=command, width=20)
            button.pack(pady=10)

        # Kreiraj desni okvir za sliku i gumbe (paralelno izvršavanje)
        self.image_canvas_parallel = create_image_frame(right_frame)

        # Kreiraj okvir za gumbe s desne strane uz scrollbar
        button_frame_canvas_parallel = tk.Canvas(right_frame, bg='#FFF8DC', highlightthickness=0)
        button_frame_canvas_parallel.pack(side='right', fill='y', expand=False)

        #scrollbar_parallel = tk.Scrollbar(right_frame, orient="vertical", command=button_frame_canvas_parallel.yview)
        #scrollbar_parallel.pack(side="right", fill="y")

        button_frame_parallel = tk.Frame(button_frame_canvas_parallel, bg='#FFF8DC')
        button_frame_parallel.pack(anchor='ne')  # Postavljamo anchor na 'ne' kako bismo postavili button_frame_parallel u gornji desni ugao button_frame_canvas_parallel

        #button_frame_canvas_parallel.configure(yscrollcommand=scrollbar_parallel.set)

        button_frame_parallel.bind("<Configure>", lambda e: button_frame_canvas_parallel.configure(scrollregion=button_frame_canvas_parallel.bbox("all")))

        # Kreiraj gumbe i grupiraj ih po funkcionalnosti
        buttons_right = [
            ("Upload Image", self.upload_image_parallel),
            ("Reset", self.reset_image_parallel),
            ("Save Image", self.save_image_parallel),
            ("Increase Saturation", lambda: self.increase_saturation_parallel(4)),
            ("Reduce Saturation", self.reduce_saturation_parallel),
            ("Blue", lambda: self.apply_color_filter_parallel('blue')),
            ("Red", lambda: self.apply_color_filter_parallel('red')),
            ("Green", lambda: self.apply_color_filter_parallel('green')),
            ("Rotate", self.rotate_image_parallel),
            ("Crop", self.start_crop_parallel),
            ("Flip", self.flip_parallel),
            ("Blur", self.blurr_parallel),
            ("Undo", self.undo_parallel),
            ("Redo", self.redo_parallel)
        ]

        for text, command in buttons_right:
            button = ttk.Button(button_frame_parallel, text=text, command=command, width=20)
            button.pack(pady=10)

        # # Vertikalno centriranje dugmadi u button_frame
        # button_frame.pack(expand=True, pady=(screen_height - len(buttons_left) * 70) // 2)  # Ovde se 70 odnosi na visinu svakog dugmeta

        # # Vertikalno centriranje dugmadi u button_frame_parallel
        # button_frame_parallel.pack(expand=True, pady=(screen_height - len(buttons_right) * 70) // 2)  # Ovde se 70 odnosi na visinu svakog dugmeta


        # Inicijalizacija slike i povijesti za serijsko izvršavanje
        self.image = None
        self.image_history = []
        self.history_index = -1

        # Inicijalizacija slike i povijesti za paralelno izvršavanje
        self.image_parallel = None
        self.image_history_parallel = []
        self.history_index_parallel = -1


    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.image_history = [self.image.copy()]
            self.history_index = 0
            self.display_image()

    def upload_image_parallel(self): # ADDED
        file_path = filedialog.askopenfilename() # ADDED
        if file_path: # ADDED
            self.image_parallel = Image.open(file_path) # ADDED
            self.image_history_parallel = [self.image_parallel.copy()] # ADDED
            self.history_index_parallel = 0 # ADDED
            self.display_image_parallel() # ADDED

    def display_image(self):
        if self.image:
            img=self.image
            self.image_canvas.delete("all")
 
            # Prilagodite veličinu slike na temelju širine image_canvas
            if(img.height<=img.width):
                imgratio = img.height / img.width
                img = img.resize((600, int(600 * imgratio)))
                canvas_width = img.width
                canvas_height =int(canvas_width * imgratio)
            else:
                imgratio = img.width / img.height
                img = img.resize((int(800 * imgratio),800))
                canvas_height = img.height
                canvas_width =int(canvas_height * imgratio)
  
            #new_width=int(self.fix#ed_height*self.image.width/self.image.height)
            # Set the image size to match the canvas width and height
          
            self.image_canvas.config(width=canvas_width, height=canvas_height)

            # Set the image in the center of the canvas
            image_width, image_height =img.size
            x_offset = (canvas_width - image_width) / 2
            y_offset = (canvas_height - image_height) / 2
            self.photo = ImageTk.PhotoImage(img)

            self.image_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)



    def display_image_parallel(self): # ADDED
        if self.image_parallel:
            img=self.image_parallel
            self.image_canvas_parallel.delete("all")

            # Prilagodite veličinu slike na temelju širine image_canvas
            if(img.height<=img.width):
                imgratio = img.height / img.width
                img = img.resize((600, int(600 * imgratio)))
                canvas_width = img.width
                canvas_height =int(canvas_width * imgratio)
            else:
                imgratio = img.width / img.height
                img = img.resize((int(800 * imgratio),800))
                canvas_height = img.height
                canvas_width =int(canvas_height * imgratio)
    
            #new_width=int(self.fix#ed_height*self.image.width/self.image.height)
            # Set the image size to match the canvas width and height
          
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

    def reset_image_parallel(self): # ADDED
        if self.image_history_parallel: # ADDED
            self.image_parallel = self.image_history_parallel[0] # ADDED
            self.history_index_parallel = 0 # ADDED
            self.display_image_parallel() # ADDED

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.image.save(file_path)

    def save_image_parallel(self): # ADDED
        if self.image_parallel: # ADDED
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]) # ADDED
            if file_path: # ADDED
                self.image_parallel.save(file_path) # ADDED

    def increase_saturation(self):
        if self.image:
            start_time = time.time()  # Start timing
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(1.5)
            end_time = time.time()  # End timing
            duration = end_time - start_time
            print(f"Time taken to apply saturation serial: {duration:.4f} seconds")
            self.update_history()
            self.display_image()


    def enhance_color(self, image_part, factor):
        # Obrada dela slike
        enhancer = ImageEnhance.Color(image_part)
        processed_part = enhancer.enhance(factor)
        return processed_part

    # def split_image(self, num_parts):
    #     # Računanje dimenzija delova slike
    #     width, height = self.image_parallel.size
    #     part_height = height // num_parts
        
    #     # Deljenje slike na delove
    #     image_parts = []
    #     for i in range(num_parts):
    #         upper = i * part_height
    #         lower = (i + 1) * part_height if i < num_parts - 1 else height
    #         part = self.image_parallel.crop((0, upper, width, lower))
    #         image_parts.append(part)
        
    #     return image_parts

    # def merge_image_parts(self, image_parts):
    #     # Spajanje delova slike u jednu
    #     if not image_parts:
    #         return None
        
    #     width, height = image_parts[0].size
    #     merged_image = Image.new("RGB", (width, height * len(image_parts)))
    #     for i, part in enumerate(image_parts):
    #         merged_image.paste(part, (0, i * height))
        
    #     return merged_image



    # def increase_saturation_parallel(self, num_parts):
    #     if self.image_parallel:
    #         start_time = time.time()  # Start timing
    #         enhancer = ImageEnhance.Color(self.image_parallel)
    #         self.image_parallel = enhancer.enhance(1.5)
    #         end_time = time.time()  # End timing
    #         duration = end_time - start_time
    #         print(f"Time taken to apply saturation serial: {duration:.4f} seconds")
    #         self.update_history_parallel()
            # self.display_image_parallel()


        #     start_time_par = time.time()  # Start timing
        #     self.image_parallel = self.pool.apply_async(self.enhance_color, (self.image_parallel, 1.5))
        #     self.image_parallel = self.image_parallel.get()  # Wait for the result
        #     end_time_par = time.time()  # End timing
        #     duration_par = end_time_par - start_time_par
        #     print(f"Time taken to apply saturation parallel: {duration_par:.4f} seconds")
        #     self.update_history_parallel()
        #     self.display_image_parallel()

        # image_parts = self.split_image(num_parts)
        
        # start_time = time.time()  # Start timing
        # processed_parts = [self.pool.apply_async(self.enhance_color, (part, 1.5)) for part in image_parts]
        # processed_parts = [part.get() for part in processed_parts]  # Wait for all results
        # end_time = time.time()  # End timing
        # duration = end_time - start_time

        # processed_image = self.merge_image_parts(processed_parts)
        
        # print(f"Time taken to apply saturation parallel: {duration:.4f} seconds")
        # processed_image.show()
        # # print("a")
    def increase_saturation_parallel(self, num_parts):
        if not self.image_parallel:
            return
        
        # Split the image into parts
        image_parts = self.split_image(num_parts)
        
        start_time = time.time()  # Start timing
        
        # Process each part in parallel
        with ThreadPoolExecutor() as executor:
            futures = []
            for part in image_parts:
                futures.append(executor.submit(self.process_part, part))
            
            processed_parts = []
            for future in as_completed(futures):
                processed_parts.append(future.result())
        
        # Merge processed parts back into a single image
        self.image_parallel = self.merge_image_parts(processed_parts)
        
        end_time = time.time()  # End timing
        duration = end_time - start_time
        print(f"Time taken to apply saturation parallel: {duration:.4f} seconds")
        
        # Update history and display the final image
        self.update_history_parallel()
        self.display_image_parallel()
    
    def process_part(self, part):
        # Apply saturation enhancement to a part of the image
        enhancer = ImageEnhance.Color(part)
        processed_part = enhancer.enhance(1.5)
        return processed_part
    
    def split_image(self, num_parts):
        # Calculate dimensions of parts
        width, height = self.image_parallel.size
        part_height = height // num_parts
        
        # Split image into parts
        image_parts = []
        for i in range(num_parts):
            upper = i * part_height
            lower = (i + 1) * part_height if i < num_parts - 1 else height
            part = self.image_parallel.crop((0, upper, width, lower))
            image_parts.append(part)
        
        return image_parts
    
    def merge_image_parts(self, image_parts):
        # Merge parts into a single image
        if not image_parts:
            return None
        
        width, height = image_parts[0].size
        merged_image = Image.new("RGB", (width, height * len(image_parts)))
        for i, part in enumerate(image_parts):
            merged_image.paste(part, (0, i * height))
        
        return merged_image

    def reduce_saturation(self):
        if self.image:
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(0.5)
            self.update_history()
            self.display_image()

    def reduce_saturation_parallel(self): # ADDED
        if self.image_parallel: # ADDED
            enhancer = ImageEnhance.Color(self.image_parallel) # ADDED
            self.image_parallel = enhancer.enhance(0.5) # ADDED
            self.update_history_parallel() # ADDED
            self.display_image_parallel() # ADDED

    def apply_color_filter(self, color):
        if self.image:
            r, g, b = self.image.split()
            if color == 'red':
                r = r.point(lambda p: p * 1.5)
            elif color == 'green':
                g = g.point(lambda p: p * 1.5)
            elif color == 'blue':
                b = b.point(lambda p: p * 1.5)
            self.image = Image.merge('RGB', (r, g, b))
            self.update_history()
            self.display_image()

    def apply_color_filter_parallel(self, color): # ADDED
        if self.image_parallel: # ADDED
            r, g, b = self.image_parallel.split() # ADDED
            if color == 'red': # ADDED
                r = r.point(lambda p: p * 1.5) # ADDED
            elif color == 'green': # ADDED
                g = g.point(lambda p: p * 1.5) # ADDED
            elif color == 'blue': # ADDED
                b = b.point(lambda p: p * 1.5) # ADDED
            self.image_parallel = Image.merge('RGB', (r, g, b)) # ADDED
            self.update_history_parallel() # ADDED
            self.display_image_parallel() # ADDED


    def rotate_image(self):
        if self.image:
            img=self.image
            height=img.height
            width=img.width
            img = img.transpose(Image.ROTATE_90)
            self.image=img
            self.update_history()

            self.display_image()

    def rotate_image_parallel(self): # ADDED
        if self.image_parallel: # ADDED
            self.image_parallel = self.image_parallel.rotate(90,resample=Image.LANCZOS, expand=True) # ADDED
            self.update_history_parallel() # ADDED
            self.display_image_parallel() # ADDED

    def start_crop(self):
        if self.image:
            self.image_canvas.bind("<ButtonPress-1>", self.on_crop_button_press)
            self.image_canvas.bind("<B1-Motion>", self.on_crop_button_move)
            self.image_canvas.bind("<ButtonRelease-1>", self.on_crop_button_release)

    def start_crop_parallel(self): # ADDED
        if self.image_parallel: # ADDED
            self.image_canvas_parallel.bind("<ButtonPress-1>", self.on_crop_button_press_parallel) # ADDED
            self.image_canvas_parallel.bind("<B1-Motion>", self.on_crop_button_move_parallel) # ADDED
            self.image_canvas_parallel.bind("<ButtonRelease-1>", self.on_crop_button_release_parallel) # ADDED

    def on_crop_button_press(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        self.crop_rectangle = self.image_canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_start_x, self.crop_start_y, outline='red')

    def on_crop_button_press_parallel(self, event): # ADDED
        self.crop_start_x_parallel = event.x # ADDED
        self.crop_start_y_parallel = event.y # ADDED
        self.crop_rectangle_parallel = self.image_canvas_parallel.create_rectangle(self.crop_start_x_parallel, self.crop_start_y_parallel, self.crop_start_x_parallel, self.crop_start_y_parallel, outline='red') # ADDED

    def on_crop_button_move(self, event):
        curX, curY = (event.x, event.y)
        self.image_canvas.coords(self.crop_rectangle, self.crop_start_x, self.crop_start_y, curX, curY)

    def on_crop_button_move_parallel(self, event): # ADDED
        curX, curY = (event.x, event.y) # ADDED
        self.image_canvas_parallel.coords(self.crop_rectangle_parallel, self.crop_start_x_parallel, self.crop_start_y_parallel, curX, curY) # ADDED

    def on_crop_button_release(self, event):
        self.crop_end_x, self.crop_end_y = (event.x, event.y)
        self.image_canvas.unbind("<ButtonPress-1>")
        self.image_canvas.unbind("<B1-Motion>")
        self.image_canvas.unbind("<ButtonRelease-1>")
        self.crop_image()

    def on_crop_button_release_parallel(self, event): # ADDED
        self.crop_end_x_parallel, self.crop_end_y_parallel = (event.x, event.y) # ADDED
        self.image_canvas_parallel.unbind("<ButtonPress-1>") # ADDED
        self.image_canvas_parallel.unbind("<B1-Motion>") # ADDED
        self.image_canvas_parallel.unbind("<ButtonRelease-1>") # ADDED
        self.crop_image_parallel() # ADDED

    def crop_image(self):
        if self.image:
        #     cropped_image = self.image.crop((self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y))
        #     self.image = cropped_image
        #     self.update_history()
        #     self.display_image()
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
            self.update_history()
            self.display_image()

    def crop_image_parallel(self): # ADDED
        if self.image_parallel: # ADDED
            cropped_image_parallel = self.image_parallel.crop((self.crop_start_x_parallel, self.crop_start_y_parallel, self.crop_end_x_parallel, self.crop_end_y_parallel)) # ADDED
            self.image_parallel = cropped_image_parallel # ADDED
            self.update_history_parallel() # ADDED
            self.display_image_parallel() # ADDED

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.image_history[self.history_index]
            self.display_image()

    def undo_parallel(self): # ADDED
        if self.history_index_parallel > 0: # ADDED
            self.history_index_parallel -= 1 # ADDED
            self.image_parallel = self.image_history_parallel[self.history_index_parallel] # ADDED
            self.display_image_parallel() # ADDED

    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.image = self.image_history[self.history_index]
            self.display_image()

    def redo_parallel(self): # ADDED
        if self.history_index_parallel < len(self.image_history_parallel) - 1: # ADDED
            self.history_index_parallel += 1 # ADDED
            self.image_parallel = self.image_history_parallel[self.history_index_parallel] # ADDED
            self.display_image_parallel() # ADDED

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
            self.image = self.image.transpose((Image.FLIP_LEFT_RIGHT))
            self.display_image()

    def flip_parallel(self):
        if(self.image):
            self.image = self.image.transpose((Image.FLIP_LEFT_RIGHT))
            self.display_image()

    def blurr(self):
        if(self.image):
            self.image = self.image.filter((ImageFilter.GaussianBlur(radius=8)))
            self.display_image()

    def blurr_parallel(self):
        if(self.image):
            self.image = self.image.filter((ImageFilter.GaussianBlur(radius=8)))
            self.display_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageUploaderApp(root)
    root.mainloop()
