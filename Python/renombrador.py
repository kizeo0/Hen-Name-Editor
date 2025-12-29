import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import subprocess
import shutil
import glob
import time
import re
import webbrowser
import sys  # <--- IMPORTANTE: Necesario para PyInstaller

# --- FUNCIÓN PARA GESTIONAR RUTAS EN EL EXE ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- CONFIGURACIÓN DE RUTAS (Modificadas con resource_path) ---
DIR_HEN_OFICIAL = resource_path("HEN OFICIAL")
DIR_AUTOHEN = resource_path("AUTOHEN")
DIR_ORIGINALES_PKG = resource_path("originales pkg")
DIR_IMAGENES = resource_path("imagenes")

# --- COLORES Y ESTILOS ---
COLOR_DEFAULT = "#f0f0f0"

# Estilos OFICIAL (Azul)
COLOR_OFICIAL_BG = "#e3f2fd"  
COLOR_OFICIAL_BTN = "#2196f3" 

# Estilos AUTOHEN (Verde Limón)
COLOR_AUTOHEN_BG = "#f9fbe7"
COLOR_AUTOHEN_BTN = "#827717"

FONT_TITLE = ("Helvetica", 14, "bold")
FONT_NORMAL = ("Helvetica", 11)

class HenRenamerPkgApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HEN NAME EDITOR - v1.0  (By KiZeo)")
        self.root.geometry("650x700")
        self.root.resizable(False, False)
        
        self.hen_version = None 
        self.current_image = None 
        
        # --- DEFINICIÓN DE RUTAS ---
        self.dir_backup_oficial = os.path.join(DIR_HEN_OFICIAL, "xml 4.92 original")
        self.dir_backup_autohen = os.path.join(DIR_AUTOHEN, "XML AUTOHEN ORIGINAL")

        self.xml_original_oficial = os.path.join(self.dir_backup_oficial, "hen_enable.xml")
        self.xml_original_autohen = os.path.join(self.dir_backup_autohen, "category_game.xml")

        self.dest_pkg_oficial = os.path.join(DIR_HEN_OFICIAL, "HACER PKG", "custom", "dev_hdd0", "hen", "xml", "hen_enable.xml")
        self.dest_pkg_autohen = os.path.join(DIR_AUTOHEN, "HACER PKG", "custom", "dev_rewrite", "vsh", "resource", "explore", "xmb", "category_game.xml")

        # --- INTERFAZ GRÁFICA ---
        
        # 1. Marco Principal
        self.main_frame = tk.Frame(root, bg=COLOR_DEFAULT)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        tk.Label(self.main_frame, text="1. SELECCIONA TU VERSIÓN", font=FONT_TITLE, bg=COLOR_DEFAULT).pack(pady=(10, 5))
        
        # Botones de Selección
        frame_select = tk.Frame(self.main_frame, bg=COLOR_DEFAULT)
        frame_select.pack(pady=10)
        
        self.btn_oficial = tk.Button(frame_select, text="HEN OFICIAL (4.92)", command=lambda: self.set_version("OFICIAL"), 
                                     font=FONT_NORMAL, width=20, height=2, bg="#ddd")
        self.btn_oficial.pack(side=tk.LEFT, padx=15)
        
        self.btn_autohen = tk.Button(frame_select, text="AUTOHEN (4.92)", command=lambda: self.set_version("AUTOHEN"), 
                                     font=FONT_NORMAL, width=20, height=2, bg="#ddd")
        self.btn_autohen.pack(side=tk.LEFT, padx=15)

        # Etiqueta de Estado
        self.lbl_status = tk.Label(self.main_frame, text="Esperando selección...", font=("Helvetica", 12, "italic"), fg="grey", bg=COLOR_DEFAULT)
        self.lbl_status.pack(pady=15)

        tk.Frame(self.main_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=10)

        # Sección de Acción Principal
        tk.Label(self.main_frame, text="2. EDICIÓN Y CREACIÓN", font=FONT_TITLE, bg=COLOR_DEFAULT).pack(pady=(10, 5))
        
        self.btn_action = tk.Button(self.main_frame, text="Editar Nombre y Crear PKG", command=self.process_renaming, 
                                    font=("Helvetica", 12, "bold"), bg="silver", fg="white", height=2, state="disabled")
        self.btn_action.pack(fill="x", padx=40, pady=10)

        tk.Frame(self.main_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=20)

        # Sección de Restauración
        tk.Label(self.main_frame, text="3. RESTAURACIÓN", font=("Helvetica", 10, "bold"), fg="#d32f2f", bg=COLOR_DEFAULT).pack(pady=(5, 5))
        
        frame_restore = tk.Frame(self.main_frame, bg=COLOR_DEFAULT)
        frame_restore.pack(pady=5)

        tk.Button(frame_restore, text="Restaurar XML Original", command=self.restore_xml, bg="#ffe0b2", width=25).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_restore, text="Restaurar PKG Original", command=self.restore_pkg, bg="#ffccbc", width=25).pack(side=tk.LEFT, padx=5)

        # --- SECCIÓN DE ICONOS ---
        self.lbl_icon = tk.Label(self.main_frame, bg=COLOR_DEFAULT)
        self.lbl_icon.pack(pady=15)
        
        # Etiqueta pequeña de ayuda (opcional)
        self.lbl_hint = tk.Label(self.main_frame, text="", font=("Arial", 8, "italic"), bg=COLOR_DEFAULT, fg="grey")
        self.lbl_hint.pack(pady=0)
        # -------------------------

        # Footer
        tk.Label(self.main_frame, text="By Kizeo - v1.0", font=("Arial", 8), bg=COLOR_DEFAULT).pack(side=tk.BOTTOM, pady=10)

    def set_version(self, version):
        self.hen_version = version
        
        image_filename = ""
        target_url = ""
        
        if version == "OFICIAL":
            bg_color = COLOR_OFICIAL_BG
            btn_color = COLOR_OFICIAL_BTN
            image_filename = "henoficial.png"
            target_url = "http://ps3xploit.me"
            self.lbl_status.config(text="Modo: HEN OFICIAL seleccionado", fg=COLOR_OFICIAL_BTN)
        else:
            bg_color = COLOR_AUTOHEN_BG
            btn_color = COLOR_AUTOHEN_BTN
            image_filename = "autohen.png"
            target_url = "https://videogamesscz.github.io/videohost/"
            self.lbl_status.config(text="Modo: AUTOHEN seleccionado", fg=COLOR_AUTOHEN_BTN)

        # Actualizar estilos
        self.main_frame.config(bg=bg_color)
        self.btn_oficial.config(bg="#ddd", relief="raised")
        self.btn_autohen.config(bg="#ddd", relief="raised")
        
        if version == "OFICIAL":
            self.btn_oficial.config(bg="white", relief="sunken", bd=3)
        else:
            self.btn_autohen.config(bg="white", relief="sunken", bd=3)

        self.btn_action.config(state="normal", bg=btn_color, fg="white")
        
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Frame):
                widget.config(bg=bg_color)
        
        # --- CARGAR IMAGEN Y ASIGNAR LINK ---
        try:
            img_path = os.path.join(DIR_IMAGENES, image_filename)
            if os.path.exists(img_path):
                self.current_image = tk.PhotoImage(file=img_path)
                
                # Configuramos la imagen y cambiamos el cursor a "mano"
                self.lbl_icon.config(image=self.current_image, bg=bg_color, cursor="hand2")
                
                # Bind (Vincular) el clic izquierdo a abrir la URL
                self.lbl_icon.bind("<Button-1>", lambda e: webbrowser.open(target_url))
                
                self.lbl_hint.config(text="(Click en la imagen para visitar la web)", bg=bg_color)
            else:
                self.lbl_icon.config(text=f"(Imagen no encontrada: {image_filename})", image="", bg=bg_color, cursor="")
                self.lbl_icon.unbind("<Button-1>")
                self.lbl_hint.config(text="", bg=bg_color)
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.lbl_icon.config(text="(Error al cargar imagen)", image="", bg=bg_color)
        # ------------------------------------

    def get_current_name_from_xml(self, xml_path):
        if not os.path.exists(xml_path):
            return ""
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'<Pair key="title">\s*<String>(.*?)</String>\s*</Pair>', content)
            if match:
                return match.group(1)
            if "Enable HEN" in content:
                return "★ Enable HEN"
            return ""
        except:
            return ""

    def process_renaming(self):
        if not self.hen_version:
            messagebox.showwarning("Aviso", "Primero selecciona HEN OFICIAL o AUTOHEN.")
            return

        if self.hen_version == "OFICIAL":
            xml_target = self.dest_pkg_oficial
            pkg_dir = os.path.join(DIR_HEN_OFICIAL, "HACER PKG")
        else:
            xml_target = self.dest_pkg_autohen
            pkg_dir = os.path.join(DIR_AUTOHEN, "HACER PKG")

        current_name = self.get_current_name_from_xml(xml_target)
        if not current_name:
            current_name = "★ Enable HEN"

        new_name = simpledialog.askstring(
            "Editar Nombre", 
            f"Edita el nombre como desees.\nBorra la estrella (★) si no la quieres:", 
            initialvalue=current_name,
            parent=self.root
        )

        if not new_name:
            return 

        if self.modify_xml(xml_target, new_name):
            safe_filename = "".join([c for c in new_name if c.isalnum() or c in (' ', '_', '-')]).strip()
            self.run_make_pkg(pkg_dir, safe_filename)

    def modify_xml(self, xml_path, new_name):
        try:
            if not os.path.exists(xml_path):
                messagebox.showerror("Error", f"No se encuentra el XML en:\n{xml_path}")
                return False

            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = r'(<Pair key="title">\s*<String>)(.*?)(</String>\s*</Pair>)'
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, f'\g<1>{new_name}\g<3>', content)
            else:
                if "Enable HEN" in content:
                    new_content = content.replace("Enable HEN", new_name)
                elif "Holis" in content:
                     new_content = content.replace("Holis", new_name)
                else:
                    messagebox.showerror("Error", "No se encontró la etiqueta de título en el XML.")
                    return False

            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
            
        except Exception as e:
            messagebox.showerror("Error XML", str(e))
            return False

    def run_make_pkg(self, pkg_dir, user_name):
        bat_file = "make_package.bat" if os.path.exists(os.path.join(pkg_dir, "make_package.bat")) else "make.bat"
        bat_path = os.path.join(pkg_dir, bat_file)
        
        if not os.path.exists(bat_path):
            messagebox.showerror("Error", f"No se encuentra {bat_file} en {pkg_dir}")
            return

        try:
            # IMPORTANTE: El CWD es pkg_dir (dentro de _MEIPASS), pero el output final
            # lo moveremos al directorio de trabajo actual (os.getcwd())
            process = subprocess.Popen(
                [bat_file], 
                cwd=pkg_dir, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True, 
                shell=True
            )
            
            try:
                stdout, stderr = process.communicate(input="\n\n\n\n\n", timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()

            time.sleep(1)
            
            pkgs = glob.glob(os.path.join(pkg_dir, "*.pkg"))
            if not pkgs:
                messagebox.showerror("Error", "El BAT terminó pero no se encontró ningún PKG nuevo.")
                return
            
            latest_pkg = max(pkgs, key=os.path.getctime)
            
            prefix = ""
            if self.hen_version == "OFICIAL":
                prefix = "HEN_oficial_"
            else:
                prefix = "AutoHen_"
            
            final_name = f"{prefix}{user_name}.pkg"

            # Destino final: Donde el usuario tiene el EXE
            dest_path = os.path.join(os.getcwd(), final_name)
            
            if os.path.exists(dest_path):
                os.remove(dest_path)
                
            shutil.move(latest_pkg, dest_path)
            messagebox.showinfo("Éxito", f"PKG Creado exitosamente:\n{final_name}")

        except Exception as e:
            messagebox.showerror("Error Compilación", str(e))

    def restore_xml(self):
        try:
            if not self.hen_version:
                messagebox.showwarning("Aviso", "Selecciona una versión primero.")
                return
            
            if self.hen_version == "OFICIAL":
                shutil.copy(self.xml_original_oficial, self.dest_pkg_oficial)
            else:
                shutil.copy(self.xml_original_autohen, self.dest_pkg_autohen)
            messagebox.showinfo("Restaurar", "XML restaurado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def restore_pkg(self):
        if not self.hen_version:
            messagebox.showwarning("Aviso", "Selecciona primero una versión (HEN OFICIAL o AUTOHEN).")
            return

        pkg_oficial_name = "Hen Oficial Nombre Original 492.pkg"
        pkg_autohen_name = "AutoHen Nombre Original 492.pkg"

        try:
            if self.hen_version == "OFICIAL":
                src_pkg = os.path.join(DIR_ORIGINALES_PKG, pkg_oficial_name)
                dest_name = pkg_oficial_name
            else:
                src_pkg = os.path.join(DIR_ORIGINALES_PKG, pkg_autohen_name)
                dest_name = pkg_autohen_name

            if not os.path.exists(src_pkg):
                messagebox.showerror("Error", f"No se encuentra el archivo original:\n{src_pkg}")
                return

            dest_path = os.path.join(os.getcwd(), dest_name)
            shutil.copy(src_pkg, dest_path)

            messagebox.showinfo("Restaurado", f"PKG Original restaurado:\n{dest_name}")

        except Exception as e:
            messagebox.showerror("Error al restaurar PKG", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    
    # --- ICONO AGREGADO AQUÍ PARA LA VENTANA ---
    try:
        root.iconbitmap(resource_path("logo.ico"))
    except Exception as e:
        print(f"No se pudo cargar el icono: {e}")
    # ------------------------------------------

    app = HenRenamerPkgApp(root)
    root.mainloop()
