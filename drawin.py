import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import math
import os
import time
from pathlib import Path

class SplashScreen:
    def __init__(self, root, image_path, duration=2000):
        self.root = root
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Center the splash screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Load splash image
        try:
            self.image = Image.open(image_path)
            img_width, img_height = self.image.size
            x = (screen_width - img_width) // 2
            y = (screen_height - img_height) // 2
            
            self.root.geometry(f"{img_width}x{img_height}+{x}+{y}")
            self.tk_image = ImageTk.PhotoImage(self.image)
            
            label = tk.Label(root, image=self.tk_image)
            label.pack()
            
            # Close after duration
            root.after(duration, root.destroy)
        except Exception as e:
            print(f"Error loading splash image: {e}")
            root.destroy()

class DrawinApp:
    def __init__(self, root, icon_path=None):
        self.root = root
        
        # Configurar icono
        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                root.iconphoto(True, photo)
            except Exception as e:
                print(f"Error loading icon: {e}")
        
        self.root.title("Drawin - Dibuja y Transforma")
        self.root.geometry("550x700")
        self.root.configure(bg='#f0f0f0')
        
        # Frame de herramientas mejorado
        self.tool_frame = tk.Frame(root, bg='#e0e0e0', padx=5, pady=5)
        self.tool_frame.pack(fill=tk.X)
        
        # Lienzo de dibujo más grande
        self.canvas = tk.Canvas(root, width=500, height=500, bg='white', 
                            highlightthickness=1, highlightbackground='#cccccc')
        self.canvas.pack(pady=10)
        
        # Botones con mejor estilo
        button_style = {'bg': '#ffffff', 'relief': tk.FLAT, 'padx': 8, 'pady': 4}
        
        self.btn_clear = tk.Button(self.tool_frame, text="🧹 Limpiar", 
                                 command=self.clear_canvas, **button_style)
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        self.btn_guess = tk.Button(self.tool_frame, text="🔍 Adivinar", 
                                 command=self.guess_drawing, **button_style)
        self.btn_guess.pack(side=tk.LEFT, padx=5)
        
        self.btn_transform = tk.Button(self.tool_frame, text="✨ Transformar", 
                                    command=self.transform_drawing, 
                                    bg='#4CAF50', fg='white', relief=tk.FLAT, padx=8, pady=4)
        self.btn_transform.pack(side=tk.LEFT, padx=5)
        
        self.btn_save = tk.Button(self.tool_frame, text="💾 Guardar", 
                                command=self.save_drawing, 
                                bg='#2196F3', fg='white', relief=tk.FLAT, padx=8, pady=4)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        # Etiqueta de estado mejorada
        self.status = tk.Label(root, text="Dibuja algo y haz clic en Adivinar", 
                            bg='#f0f0f0', fg='#555555', font=('Arial', 10))
        self.status.pack()
        
        # Variables de dibujo
        self.drawing = False
        self.last_x, self.last_y = None, None
        self.points = []
        self.current_guess = None
        self.transformed = False
        
        # Eventos
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        
        # Objetos reconocibles ampliados (15 objetos)
        self.recognizable_objects = {
            "sol": self.draw_sun,
            "luna": self.draw_moon,
            "casa": self.draw_house,
            "árbol": self.draw_tree,
            "coche": self.draw_car,
            "persona": self.draw_person,
            "gato": self.draw_cat,
            "perro": self.draw_dog,
            "flor": self.draw_flower,
            "estrella": self.draw_star,
            "corazón": self.draw_heart,
            "globo": self.draw_balloon,
            "pez": self.draw_fish,
            "mariposa": self.draw_butterfly,
            "barco": self.draw_boat
        }
        
    def start_drawing(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y
        self.points = [(event.x, event.y)]
        self.current_guess = None
        self.transformed = False
        self.status.config(text="Dibujando...")
        
    def draw(self, event):
        if self.drawing:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, 
                                width=3, fill='black', capstyle=tk.ROUND)
            self.last_x, self.last_y = event.x, event.y
            self.points.append((event.x, event.y))
            
    def stop_drawing(self, event):
        if self.drawing:
            self.drawing = False
            self.analyze_drawing()
            
    def clear_canvas(self):
        self.canvas.delete("all")
        self.points = []
        self.current_guess = None
        self.transformed = False
        self.status.config(text="Lienzo limpio. Dibuja algo nuevo.")
        
    def analyze_drawing(self):
        if len(self.points) < 3:
            return
            
        # Calcular características básicas
        min_x = min(p[0] for p in self.points)
        max_x = max(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)
        
        width = max_x - min_x
        height = max_y - min_y
        aspect_ratio = width / height if height != 0 else 1
        
        # Calcular circularidad
        centroid_x = sum(p[0] for p in self.points) / len(self.points)
        centroid_y = sum(p[1] for p in self.points) / len(self.points)
        distances = [math.sqrt((p[0]-centroid_x)**2 + (p[1]-centroid_y)**2) for p in self.points]
        avg_distance = sum(distances) / len(distances)
        circularity = sum(abs(d - avg_distance) for d in distances) / len(distances)
        
        # Detección de formas mejorada
        if circularity < 15 and 0.7 < aspect_ratio < 1.3:
            self.current_guess = "sol"
        elif circularity < 20 and aspect_ratio > 1.5:
            self.current_guess = "coche"
        elif circularity < 20 and aspect_ratio < 0.7:
            self.current_guess = "árbol"
        elif self.is_house_shape():
            self.current_guess = "casa"
        elif self.is_star_shape():
            self.current_guess = "estrella"
        elif self.is_heart_shape():
            self.current_guess = "corazón"
        elif self.is_balloon_shape():
            self.current_guess = "globo"
        elif self.is_fish_shape():
            self.current_guess = "pez"
            
    def is_house_shape(self):
        if len(self.points) < 10:
            return False
            
        angles = self.calculate_angles()
        right_angles = sum(1 for a in angles if 70 < a < 110)
        return right_angles >= 2
        
    def is_star_shape(self):
        if len(self.points) < 10:
            return False
            
        sharp_turns = 0
        angles = self.calculate_angles()
        sharp_turns = sum(1 for a in angles if a < 60)
        return sharp_turns >= 5
        
    def is_heart_shape(self):
        if len(self.points) < 10:
            return False
            
        # Verificar simetría aproximada
        centroid_x = sum(p[0] for p in self.points) / len(self.points)
        symmetric_points = 0
        threshold = 20
        
        for x, y in self.points:
            mirrored_x = 2 * centroid_x - x
            # Buscar un punto cercano al punto espejo
            for px, py in self.points:
                if abs(px - mirrored_x) < threshold and abs(py - y) < threshold:
                    symmetric_points += 1
                    break
                    
        return symmetric_points / len(self.points) > 0.6
        
    def is_balloon_shape(self):
        if len(self.points) < 5:
            return False
            
        # Verificar si tiene una parte ovalada arriba y una línea abajo
        upper_points = [p for p in self.points if p[1] < sum(p[1] for p in self.points)/len(self.points)]
        if len(upper_points) < 3:
            return False
            
        # Calcular circularidad solo para la parte superior
        centroid_x = sum(p[0] for p in upper_points) / len(upper_points)
        centroid_y = sum(p[1] for p in upper_points) / len(upper_points)
        distances = [math.sqrt((p[0]-centroid_x)**2 + (p[1]-centroid_y)**2) for p in upper_points]
        avg_distance = sum(distances) / len(distances)
        circularity = sum(abs(d - avg_distance) for d in distances) / len(distances)
        
        return circularity < 25
        
    def is_fish_shape(self):
        if len(self.points) < 10:
            return False
            
        # Verificar si tiene una cola (punto donde cambia bruscamente la dirección)
        angles = self.calculate_angles()
        sharp_turns = sum(1 for a in angles if a < 45)
        return 1 <= sharp_turns <= 3
        
    def calculate_angles(self):
        angles = []
        for i in range(1, len(self.points)-1):
            x1, y1 = self.points[i-1]
            x2, y2 = self.points[i]
            x3, y3 = self.points[i+1]
            
            angle = math.degrees(math.atan2(y3-y2, x3-x2) - math.atan2(y1-y2, x1-x2))
            angle = abs(angle)
            if angle > 180:
                angle = 360 - angle
            angles.append(angle)
        return angles
        
    def guess_drawing(self):
        if not self.points:
            messagebox.showinfo("Drawin", "¡Dibuja algo primero!")
            return
            
        if self.current_guess:
            self.status.config(text=f"Creo que es un {self.current_guess}. ¡Haz clic en Transformar!")
        else:
            options = list(self.recognizable_objects.keys())
            user_guess = simpledialog.askstring("Drawin", 
                                            "No estoy seguro. ¿Qué estabas dibujando?\nOpciones: " + ", ".join(options),
                                            parent=self.root)
            if user_guess and user_guess.lower() in self.recognizable_objects:
                self.current_guess = user_guess.lower()
                self.status.config(text=f"¡Transformaré tu dibujo en un {self.current_guess}!")
            else:
                self.status.config(text="No reconozco ese objeto. Intenta con otro dibujo.")
                
    def transform_drawing(self):
        if not self.current_guess:
            messagebox.showinfo("Drawin", "Primero adivina o especifica qué es tu dibujo.")
            return
            
        self.canvas.delete("all")
        draw_function = self.recognizable_objects.get(self.current_guess)
        if draw_function:
            draw_function()
            self.transformed = True
            self.status.config(text=f"¡Voilà! Tu dibujo ahora es un {self.current_guess}. Puedes guardarlo.")
        else:
            self.canvas.create_text(250, 250, text=self.current_guess, 
                                font=('Arial', 24), fill='blue')
            self.transformed = True
            
    def save_drawing(self):
        if not self.transformed:
            messagebox.showinfo("Drawin", "Primero transforma tu dibujo para guardarlo.")
            return
        
        # Obtener la carpeta de Descargas del usuario
        downloads_path = str(Path.home() / "Downloads")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"Drawin_{self.current_guess}_{timestamp}.png"
        filepath = os.path.join(downloads_path, filename)
    
        # Crear una imagen PIL del canvas
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
    
        # Capturar la pantalla del canvas
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        img.save(filepath, 'PNG')
    
        self.status.config(text=f"Dibujo guardado como {filename} en Descargas")
        messagebox.showinfo("Drawin", f"¡Dibujo guardado con éxito!\n{filepath}")
    
    # ==============================================
    # Funciones de dibujo para todos los objetos
    # ==============================================
    
    def draw_sun(self):
        self.canvas.create_oval(150, 150, 350, 350, fill='yellow', outline='orange', width=2)
        for i in range(0, 360, 30):
            rad = math.radians(i)
            x1 = 250 + 110 * math.cos(rad)
            y1 = 250 + 110 * math.sin(rad)
            x2 = 250 + 140 * math.cos(rad)
            y2 = 250 + 140 * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill='orange')
        
    def draw_moon(self):
        self.canvas.create_oval(175, 150, 325, 300, fill='#f0f0f0', outline='gray', width=2)
        self.canvas.create_oval(200, 150, 300, 300, fill='white', outline='white')
        
    def draw_house(self):
        # Base de la casa
        self.canvas.create_rectangle(175, 250, 325, 350, fill='#FFD700', outline='brown', width=2)
        # Techo
        self.canvas.create_polygon(160, 250, 340, 250, 250, 170, fill='red', outline='brown', width=2)
        # Puerta
        self.canvas.create_rectangle(230, 280, 270, 350, fill='brown', outline='black', width=1)
        # Ventanas
        self.canvas.create_rectangle(190, 270, 220, 300, fill='#87CEEB', outline='black', width=1)
        self.canvas.create_rectangle(280, 270, 310, 300, fill='#87CEEB', outline='black', width=1)
        
    def draw_tree(self):
        # Tronco
        self.canvas.create_rectangle(235, 300, 265, 350, fill='brown', outline='black', width=1)
        # Copa
        self.canvas.create_oval(150, 200, 350, 300, fill='green', outline='darkgreen', width=2)
        
    def draw_car(self):
        # Cuerpo
        self.canvas.create_rectangle(150, 250, 350, 280, fill='red', outline='black', width=2)
        self.canvas.create_rectangle(180, 230, 320, 250, fill='red', outline='black', width=2)
        # Ruedas
        self.canvas.create_oval(160, 270, 190, 300, fill='black')
        self.canvas.create_oval(310, 270, 340, 300, fill='black')
        
    def draw_person(self):
        # Cabeza
        self.canvas.create_oval(225, 150, 275, 200, fill='#FFD699', outline='black', width=1)
        # Cuerpo
        self.canvas.create_line(250, 200, 250, 275, width=2)
        # Brazos
        self.canvas.create_line(250, 225, 190, 240, width=2)
        self.canvas.create_line(250, 225, 310, 240, width=2)
        # Piernas
        self.canvas.create_line(250, 275, 220, 320, width=2)
        self.canvas.create_line(250, 275, 280, 320, width=2)
        
    def draw_cat(self):
        # Cabeza
        self.canvas.create_oval(200, 180, 300, 280, fill='gray', outline='black', width=1)
        # Orejas
        self.canvas.create_polygon(210, 180, 230, 140, 250, 180, fill='gray', outline='black', width=1)
        self.canvas.create_polygon(250, 180, 270, 140, 290, 180, fill='gray', outline='black', width=1)
        # Ojos
        self.canvas.create_oval(225, 210, 235, 220, fill='green', outline='black', width=1)
        self.canvas.create_oval(265, 210, 275, 220, fill='green', outline='black', width=1)
        # Nariz y boca
        self.canvas.create_polygon(245, 230, 255, 230, 250, 240, fill='pink', outline='black', width=1)
        self.canvas.create_line(250, 240, 250, 250, width=1)
        self.canvas.create_line(250, 250, 230, 260, width=1)
        self.canvas.create_line(250, 250, 270, 260, width=1)
        
    def draw_dog(self):
        # Cabeza
        self.canvas.create_oval(200, 180, 300, 280, fill='#8B4513', outline='black', width=1)
        # Orejas
        self.canvas.create_oval(200, 180, 240, 220, fill='#8B4513', outline='black', width=1)
        self.canvas.create_oval(260, 180, 300, 220, fill='#8B4513', outline='black', width=1)
        # Ojos
        self.canvas.create_oval(225, 210, 235, 220, fill='black')
        self.canvas.create_oval(265, 210, 275, 220, fill='black')
        # Nariz
        self.canvas.create_oval(245, 230, 255, 240, fill='black')
        # Boca
        self.canvas.create_line(250, 240, 250, 250, width=1)
        self.canvas.create_line(250, 250, 230, 255, width=1)
        self.canvas.create_line(250, 250, 270, 255, width=1)
        
    def draw_flower(self):
        # Tallo
        self.canvas.create_line(250, 250, 250, 350, fill='green', width=3)
        # Hojas
        self.canvas.create_oval(200, 270, 230, 300, fill='green', outline='darkgreen', width=1)
        self.canvas.create_oval(270, 300, 300, 330, fill='green', outline='darkgreen', width=1)
        # Flor
        self.canvas.create_oval(200, 200, 300, 300, fill='yellow', outline='orange', width=2)
        for i in range(0, 360, 45):
            rad = math.radians(i)
            x1 = 250 + 50 * math.cos(rad)
            y1 = 250 + 50 * math.sin(rad)
            x2 = 250 + 80 * math.cos(rad)
            y2 = 250 + 80 * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill='pink')
            
    def draw_star(self):
        points = []
        for i in range(5):
            # Puntos externos
            angle = math.radians(90 + i * 72)
            x = 250 + 80 * math.cos(angle)
            y = 250 + 80 * math.sin(angle)
            points.extend([x, y])
            
            # Puntos internos
            angle = math.radians(90 + 36 + i * 72)
            x = 250 + 30 * math.cos(angle)
            y = 250 + 30 * math.sin(angle)
            points.extend([x, y])
            
        self.canvas.create_polygon(points, fill='yellow', outline='gold', width=2)
        
    def draw_heart(self):
        points = []
        for t in range(0, 628, 10):  # 0 a 2π en pasos de 0.1 radianes
            t = t / 100
            x = 250 + 16 * math.sin(t)**3
            y = 250 - (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            points.extend([x, y])
        
        self.canvas.create_polygon(points, fill='red', outline='darkred', width=2)
        
    def draw_balloon(self):
        # Globo
        self.canvas.create_oval(200, 150, 300, 250, fill='red', outline='darkred', width=2)
        # Cuerda
        self.canvas.create_line(250, 250, 250, 300, fill='gray', width=1)
        # Canasta
        self.canvas.create_rectangle(230, 300, 270, 310, fill='brown', outline='black', width=1)
        
    def draw_fish(self):
        # Cuerpo
        self.canvas.create_oval(200, 200, 300, 250, fill='orange', outline='black', width=1)
        # Cola
        self.canvas.create_polygon(300, 225, 330, 200, 330, 250, fill='orange', outline='black', width=1)
        # Ojo
        self.canvas.create_oval(210, 215, 220, 225, fill='black')
        # Aletas
        self.canvas.create_polygon(230, 225, 250, 210, 270, 225, fill='orange', outline='black', width=1)
        self.canvas.create_polygon(230, 225, 250, 240, 270, 225, fill='orange', outline='black', width=1)
        
    def draw_butterfly(self):
        # Cuerpo
        self.canvas.create_line(250, 200, 250, 300, fill='black', width=3)
        # Alas superiores
        self.canvas.create_oval(150, 150, 250, 250, fill='purple', outline='black', width=1)
        self.canvas.create_oval(250, 150, 350, 250, fill='purple', outline='black', width=1)
        # Alas inferiores
        self.canvas.create_oval(170, 220, 250, 300, fill='blue', outline='black', width=1)
        self.canvas.create_oval(250, 220, 330, 300, fill='blue', outline='black', width=1)
        # Antenas
        self.canvas.create_line(250, 200, 230, 170, fill='black', width=1)
        self.canvas.create_line(250, 200, 270, 170, fill='black', width=1)
        
    def draw_boat(self):
        # Casco
        self.canvas.create_polygon(200, 300, 300, 300, 280, 270, 220, 270, fill='brown', outline='black', width=2)
        # Vela
        self.canvas.create_polygon(250, 270, 250, 200, 300, 270, fill='white', outline='black', width=1)
        # Mástil
        self.canvas.create_line(250, 270, 250, 180, fill='brown', width=3)
        # Bandera
        self.canvas.create_rectangle(250, 180, 270, 190, fill='red', outline='black', width=1)

# Configuración inicial
if __name__ == "__main__":
    root = tk.Tk()
    
    # Mostrar splash screen (asegúrate de tener el archivo splash.png en el mismo directorio)
    splash_image = "drawin_splash.png"  # Ruta del archivo de splash
    if os.path.exists(splash_image):
        splash = SplashScreen(tk.Toplevel(), splash_image, 2500)
        root.withdraw()  # Ocultar la ventana principal mientras se muestra el splash
        root.after(2500, root.deiconify)  # Mostrar la ventana principal después
    
    # Iniciar la aplicación principal
    app_icon = "drawin_icon.ico" # Ruta del icono de la aplicación
    app = DrawinApp(root, app_icon)
    root.mainloop()