import tkinter as tk
from tkinter import ttk,messagebox,filedialog
import  os,re,time,shutil,json
from Medicalomni3d.Captcha_medicalomni3d import CaptchaMedicalOmni3D
from Medicalomni3d.Dao_medicalomni3d import  DAOMedicalOmni3D
from Medicalomni3d.Base_datos import Conexion_Base_Datos_MedicalOmni3D
from Medicalomni3d.Usuario_medicalomni3d import  Usuario
from Medicalomni3d.Configuracion_medicalomni3d import Configuracion_ventana,Estilos,Leer_imagenes
from Medicalomni3d.Ventana_principal import Ventana_Principal_MedicalOmni3D
from Medicalomni3d.Configuracion_Apcivmapcas import Configuracionnnunetv2
import multiprocessing
import sys


if getattr(sys, "frozen", False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

try:
    from ctypes import windll
    myappid = 'andresCA.MedicalOmni3D.subproduct.0.0.1.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class MedicalOmni3D_app(tk.Tk):
    def __init__(self):
        super().__init__()
        Configuracionnnunetv2.Creacion_variables_entorno()
        self.username = None
        self.password = None
        self.boton_enviar = None
        self.boton_mostar = None
        self.entrada_password = None
        self.frame_password = None
        self.entrada_usuario = None
        self.entrada_captcha = None
        self.boton_captcha_refresh = None
        self.frame_captcha = None
        self.frame_1 = None
        self.icono_refresh = None
        self.imagen_principal = None
        self.icono_app = None
        self.imagen_captcha = None
        self.texto_captcha = None
        self.imagen_icono_monstrar = None
        self.Ventana_principal_medicalomni3d = None
        self.label_capcha=None
        self.mostrar=True
        self.Creacion_base_datos_app(ruta=Configuracionnnunetv2.BASE_DIR2)
        Estilos()
        Configuracion_ventana(self,no_modificar=True)
        self.configure(background="darkblue")
        self.Imagenes_Medicalomni3d()
        self.Inicio_Sesion()


    def Creacion_base_datos_app(self, ruta: str = None):
        if os.path.exists(ruta):
            if not os.path.isfile(os.path.join(ruta,"medicalomni3d.db")):
                Conexion_Base_Datos_MedicalOmni3D.Ruta_base_datos = ruta
                Conexion_Base_Datos_MedicalOmni3D.Creacion_baseDatos()
                Conexion_Base_Datos_MedicalOmni3D.Creacion_Tablas()
                DAOMedicalOmni3D.Crear_usuario_admin_defecto()

    def Imagen_Captcha(self,event):
        self.texto_captcha, path_captcha = CaptchaMedicalOmni3D.Generar_captcha()
        self.imagen_captcha = Leer_imagenes(path_captcha,(120,120))
        if self.label_capcha is not None:
            self.label_capcha.configure(image=self.imagen_captcha)
            self.entrada_captcha.delete(0,tk.END)


    def Imagenes_Medicalomni3d(self):
        self.icono_app = os.path.join(basedir, "Assets", "medicalomni3d.ico")
        if sys.platform.startswith("win"):
            self.iconbitmap(self.icono_app)
        else:
            self.icono_app_png = tk.PhotoImage(file=os.path.join(basedir, "Assets", "medicalomni3d.png"))
            self.iconphoto(True, self.icono_app_png)
        self.Imagen_Captcha(event=None)
        self.imagen_principal = Leer_imagenes(os.path.join(basedir, "Assets", "medicalomni3d.png"),(150,150))
        self.icono_refresh = Leer_imagenes(os.path.join(basedir, "Assets", "refresh.png"),(15,15))
        self.imagen_icono_monstrar=Leer_imagenes(os.path.join(basedir, "Assets", "visibility.png"),(15,15))

    def Frame_Inicio_Sesion(self):
        self.frame_1 = ttk.Frame(self, style="Custom.TFrame")
        self.frame_1.grid(column=0, row=0, ipadx=80, ipady=40)
        self.frame_1.columnconfigure(0, weight=1)
        self.frame_1.columnconfigure(1, weight=1)

    def Label_Inicio_Sesion(self):
        label_imagen_princiapl = tk.Label(self.frame_1, image=self.imagen_principal,bg="white",foreground="black")
        label_usuario = tk.Label(self.frame_1, text="Ingrese Usuario: ",bg="white",foreground="black")
        label_password = tk.Label(self.frame_1, text="Ingrese Contraseña: ",bg="white",foreground="black")
        label_imagen_princiapl.grid(row=0, column=0, columnspan=2, ipady=10)
        label_usuario.grid(row=1, column=0, pady=10, sticky=tk.E)
        label_password.grid(row=2,column=0,sticky=tk.E)

    def Captcha_Inicio_sesion(self):
        self.frame_captcha = ttk.Frame(self.frame_1, style="Custom.TFrame")
        self.label_capcha = ttk.Label(self.frame_1, image=self.imagen_captcha, background="black", border=0.5, relief=tk.RIDGE)
        self.label_capcha.grid(row=3, column=0, columnspan=2, pady=20)
        self.frame_captcha.grid(row=4, column=0, columnspan=2)
        self.entrada_captcha = ttk.Entry(self.frame_captcha, justify=tk.CENTER)
        self.boton_captcha_refresh = ttk.Button(self.frame_captcha, image=self.icono_refresh, width=6,command=lambda :self.Imagen_Captcha(event=None),style="Inicio_sesion.TButton")
        self.entrada_captcha.pack(side=tk.LEFT)
        self.boton_captcha_refresh.pack(side=tk.RIGHT)
        self.boton_captcha_refresh.bind("<Return>",self.Imagen_Captcha)


    def Entrada_Inicio_Sesion(self):
        self.entrada_usuario = ttk.Entry(self.frame_1,justify=tk.LEFT,width=28)
        self.entrada_usuario.grid(row=1, column=1, sticky=tk.W)
        self.frame_password = ttk.Frame(self.frame_1, style="Custom.TFrame")
        self.frame_password.grid(row=2, column=1, sticky=tk.W)
        self.entrada_password = ttk.Entry(self.frame_password,justify=tk.LEFT,show="●",width=24)
        self.boton_mostar = ttk.Button(self.frame_password,image=self.imagen_icono_monstrar,width=2,command=lambda :self.Mostrar_ocultar_password(event=None),style="Inicio_sesion.TButton")
        self.entrada_password.pack(side=tk.LEFT)
        self.boton_mostar.pack(side=tk.LEFT)
        self.boton_mostar.bind("<Return>", self.Mostrar_ocultar_password)


    def Inicio_Sesion(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.Frame_Inicio_Sesion()
        self.Entrada_Inicio_Sesion()
        self.Label_Inicio_Sesion()
        self.Captcha_Inicio_sesion()
        self.boton_enviar = ttk.Button(self.frame_1, text="Enviar", command=lambda : self.Verifica_inicio_sesion(evento=None), cursor="hand2")
        self.boton_enviar.grid(row=5, column=0, columnspan=2, pady=10)
        self.boton_enviar.bind("<Return>", self.Verifica_inicio_sesion)


    def Verificacion_Captcha(self):
        captcha=self.entrada_captcha.get().strip()
        if captcha:
            if captcha==self.texto_captcha:
                user=Usuario(username=self.username,password=self.password)
                usuario=DAOMedicalOmni3D.inicio_sesion(user)
                if usuario:
                    self.Limpiar_entradas_inicion_sesion()
                    self.withdraw()
                    self.Ventana_principal_medicalomni3d=Ventana_Principal_MedicalOmni3D(self,usuario)
                else:
                    self.Imagen_Captcha(event=None)
            else:
                messagebox.showerror("Error Captcha","Verificación CAPTCHA inválida. Intente nuevamente.")
                self.Imagen_Captcha(event=None)
        else:
            messagebox.showerror("Error Captcha", "Por favor, ingrese el código CAPTCHA")
            self.Imagen_Captcha(event=None)
    def Mostrar_ocultar_password(self,event):
        if self.mostrar:
            self.mostrar=False
            self.imagen_icono_monstrar=Leer_imagenes(os.path.join(basedir, "Assets", "visibility_off.png"), (15, 15))
            self.boton_mostar.configure(image=self.imagen_icono_monstrar)
            self.entrada_password.configure(show="")
        else:
            self.mostrar = True
            self.imagen_icono_monstrar=Leer_imagenes(os.path.join(basedir, "Assets", "visibility.png"), (15, 15))
            self.boton_mostar.configure(image=self.imagen_icono_monstrar)
            self.entrada_password.configure(show="●")

    def Verifica_inicio_sesion(self,evento):
        self.username=self.entrada_usuario.get().strip()
        self.password = self.entrada_password.get().strip()
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if self.username:
            if re.match(email_pattern,self.username):
                if self.password:
                    self.Verificacion_Captcha()
                else:
                    messagebox.showerror("Error Inicio de sesión", "Por favor, ingrese su contraseña.")
            else:
                messagebox.showerror("Error Inicio de sesión","Ingrese un correo electrónico válido.")
        else:
            messagebox.showerror("Error Inicio de sesión", "Por favor, ingrese su correo electrónico.")
    def Limpiar_entradas_inicion_sesion(self):
        self.entrada_usuario.delete(0,tk.END)
        self.entrada_password.delete(0,tk.END)
        self.entrada_captcha.delete(0,tk.END)
        self.Imagen_Captcha(event=None)

if __name__=="__main__":

    multiprocessing.freeze_support()

    if sys.platform in ['darwin', 'linux']:
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            pass

    app=MedicalOmni3D_app()
    app.mainloop()




