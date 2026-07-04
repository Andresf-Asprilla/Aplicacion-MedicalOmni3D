from tkinter import ttk
import tkinter as tk
from PIL import  ImageTk,Image
import sys,os

def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "Assets", relative_path)

def Configuracion_ventana(ventana,ancho:int = 800,alto:int = 600,titulo:str="MedicalOmni3D",no_modificar:bool=False):
    ventana.title(titulo)
    if no_modificar:
        ventana.resizable(0, 0)
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = int((pantalla_ancho / 2) - (ancho / 2))
    y = int((pantalla_alto / 2) - (alto / 2))
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.configure(background="#082B78")

def Estilos():
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Custom.TFrame",background="white")
    estilo.configure("Menu_deslizable.TFrame", background="#082B78",)
    estilo.configure("Banner.TFrame", background="#071640")
    estilo.configure("Admin.TFrame", background="#071640", borderwidth=5, relief=tk.SOLID)
    estilo.configure("Page.TFrame", background="#C7C7C7")
    estilo.configure("Banner.TLabel", background="#071640",font=(" ", 15, "bold"),foreground="white")
    estilo.configure("TFrame", background="#082B78")
    estilo.configure("TLabel", background="#082B78",foreground="white",font=(" ", 10, "bold"))
    estilo.configure("TButton",foreground="#071640",focuscolor="darkblue",padding=(2, 1))
    estilo.configure("Menu_deslizable.TButton", background="#082B78", focuscolor="none",foreground="white",focusthickness=0,borderwidth=0)
    estilo.map("Menu_deslizable.TButton",background=[("active", "#082B78")])
    estilo.configure("Indicador_menu_deslizable_onn.TLabel",background="white")
    estilo.configure("TLabelframe",background="#071640", bordercolor="white")
    estilo.configure("TLabelframe.Label",background="#071640", foreground="white")
    estilo.configure("Config.TLabel",background="#071640", foreground="white")
    estilo.configure("TCheckbutton",background="#071640",foreground="white")
    estilo.map("TCheckbutton",foreground=[("selected", "blue"),("!selected", "white"),("active", "blue"),("!active", "black")])
    estilo.configure("Indicador_menu_deslizable_off.TLabel", background="#082B78",font=(" ", 9, "bold"),foreground="white")
    estilo.configure("Menu_deslizable.TLabel", background="#082B78",font=(" ", 9, "bold"),foreground="white")
    estilo.configure("Treeview",background="#072941",font=(" ", 10, "bold"),foreground="White",fieldbackground="#072941",rowheight=28)
    estilo.configure("Page_botones.TFrame",background="#C7C7C7",borderwidth=5,relief=tk.SOLID)
    estilo.configure("Page_configuracion_banco.TFrame", background="#C7C7C7", borderwidth=5, relief=tk.FLAT)
    estilo.configure("Page_uausarios_banco.TFrame", background="#C7C7C7", borderwidth=10, relief=tk.SUNKEN)




def Leer_imagenes(paht:str=None,zise:tuple=None):
    if zise is None:
        return ImageTk.PhotoImage(Image.open(paht))
    else:
        return ImageTk.PhotoImage(Image.open(paht).resize(zise))

