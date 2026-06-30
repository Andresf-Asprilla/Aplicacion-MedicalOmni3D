import sys,platform
from PIL import Image, ImageTk
import tkinter as tk
import SimpleITK as sitk
from Medicalomni3d.Visor_medicalomni3d import Visor_MedicalOmni3D
from Medicalomni3d.loggin_MedicalOmni3d import log
from tkinter import ttk,messagebox,filedialog
from Medicalomni3d.Ventana_carga import VentanaCargaSubproceso
from Medicalomni3d.Configuracion_Apcivmapcas import Configuracionnnunetv2
from Medicalomni3d.Dao_medicalomni3d import  DAOMedicalOmni3D
from Medicalomni3d.Configuracion_medicalomni3d import Configuracion_ventana,Estilos,Leer_imagenes
import  os,re,time,shutil,json
from Medicalomni3d.Usuario_medicalomni3d import Usuario

basedir = os.path.dirname(__file__)

class Ventana_Principal_MedicalOmni3D(tk.Toplevel):
    def __init__(self,master=None,usuario=None):
        super().__init__(master)
        self.frame_visualizador = None
        self.label_username = None
        self.imagen_update_modelo = None
        self.imagen_cancelar = None
        self.imagen_export = None
        self.imagen_import = None
        self.imagen_user = None
        self.imagen_tabla = None
        self.imagen_configurar = None
        self.icono_app = None
        self.imagen_salir = None
        self.visor = None
        self.imagen_visor=None
        self.mascara=None
        self.lista_usuarios=None
        self.lista_logs=None
        self.mostrar_crear = True
        self.mostrar_editar=True
        self.email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        self.password_pattern = r'^(?=.*[A-Z])(?=.*[\d\W]).{8,}$'
        self.cambiar_password = tk.BooleanVar(value=False)
        self.withdraw()
        Configuracionnnunetv2.Creacion_variables_entorno()
        self.configuracion_sistema=Configuracionnnunetv2.Configuracion_apcivmapcas_json()
        self.dispositivo = Configuracionnnunetv2.Dispositivo_inferencia()
        print(self.configuracion_sistema,self.configuracion_sistema.keys())
        name_modelo=self.configuracion_sistema["modelo_seleccionado"]
        self.dispositivo_selecionado = self.configuracion_sistema["modelos"][name_modelo]["device"] if self.configuracion_sistema["modelo_seleccionado"]!="" else "cpu"
        self.archivojson = Configuracionnnunetv2.BASE_CONFIGURACION
        self.lista_espaciado = self.configuracion_sistema["modelos"][name_modelo]["nuevo_espaciado"] if  self.configuracion_sistema["modelo_seleccionado"] !="" else [1,1,1]
        self.normalizacion = tk.BooleanVar(value=self.configuracion_sistema["modelos"][name_modelo]["Normalizacion"] if self.configuracion_sistema["modelo_seleccionado"] !="" else True )
        self.espaciado = tk.BooleanVar(value=self.configuracion_sistema["modelos"][name_modelo]["Espaciado"]if self.configuracion_sistema["modelo_seleccionado"] !="" else True)
        self.maxtime_segundos=900
        self.ultimo_evento = time.time()
        self.usuario=usuario
        self.logs_accion=self.usuario.ACCIONES.copy()
        self.logs_accion.insert(0,"Todos")
        self.master=master
        self.mostrar_menu = True
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.columna_tabla=["ID","Imagen","Indicador de inferencia"]
        self.columna_tabla_logs=["Fecha/Hora","Usuario","Acción"]
        self.columna_tabla_usuario=["ID","Usuario","Rol","Estado","Fecha último acceso"]
        self.eleccion_modelos=None
        Estilos()
        self.Iconos_menu_deslizable()
        self.botones_menu = [{"nombre": "Banco de imágenes", "imagen": self.imagen_tabla, "y": 360,"comand":self.Frames_banco_imagenes}, {"nombre": "Configuración de Modelos", "imagen": self.imagen_configurar, "y": 420, "comand":self.Pagina_configuracion}, {"nombre": "Salir", "imagen": self.imagen_salir, "y": 480, "comand":self.Confirmar_salida}]
        self.lista_imagenes_tabla=None
        self.imagenes_codificadas=None
        self.Configuracion_ventana_principal_MedicalOmni3d()
        self.Frame_menu_deslizable()
        self.Creacion_menu_deslizable()
        self.Logo_banner()
        self.Dectectar_actividad()
        self.verificar_inactividad()
        self.after(10, self.inicializacion_completa)


    def inicializacion_completa(self):

        self.update_idletasks()

        self.deiconify()

    def cerrar_aplicacion(self):
        if hasattr(self, "visor") and self.visor is not None:
            self.visor.destruir_visor()
        DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, self.usuario.ACCIONES[2])
        Configuracionnnunetv2.Eliminacion_json_salida()
        self.master.destroy()

    def cerrar_sesion(self,event):
        if hasattr(self, "visor") and self.visor is not None:
            self.visor.destruir_visor()
        DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, self.usuario.ACCIONES[2])
        Configuracionnnunetv2.Eliminacion_json_salida()
        self.destroy()
        self.master.deiconify()
        
    def reset_timer(self, event=None):
        self.ultimo_evento = time.time()
    def Dectectar_actividad(self):
        self.bind_all("<Any-KeyPress>", self.reset_timer)
        self.bind_all("<Any-Button>", self.reset_timer)
        self.bind_all("<Motion>", self.reset_timer)

    def verificar_inactividad(self):
        tiempo_actual = time.time()

        if tiempo_actual - self.ultimo_evento > self.maxtime_segundos:
            self.cerrar_sesion(event=None)
        else:
            self.after(1000, self.verificar_inactividad)

    def Configuracion_ventana_principal_MedicalOmni3d(self):
        self.title("MedicalOmni3D")
        sistema = platform.system()
        if sistema == "Windows":
            self.iconbitmap(self.icono_app)
            self.state("zoomed")

        elif sistema == 'Darwin':
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(True, icon_photo)
            self.attributes('-fullscreen', False)
            self.wm_state('zoomed')
        else:
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(True, icon_photo)
            self.attributes('-zoomed', True)

        self.configure(background="#C7C7C7")
        pantalla_ancho =int(self.winfo_screenwidth()/1.2)
        pantalla_alto = int(self.winfo_screenheight()/1.2)
        self.minsize(width=pantalla_ancho,height=pantalla_alto)

    def Iconos_menu_deslizable(self):
        self.icono_app = os.path.join(basedir, "Assets", "medicalomni3d.ico")
        self.imagen_salir = Leer_imagenes(os.path.join(basedir, "Assets", "exit.png"),(30,30))
        self.imagen_configurar = Leer_imagenes(os.path.join(basedir, "Assets", "settings.png"),(30,30))
        self.imagen_tabla= Leer_imagenes(os.path.join(basedir, "Assets", "table_view.png"), (30, 30))
        self.imagen_user= Leer_imagenes(os.path.join(basedir, "Assets", "account_circle.png"),(30, 30))
        self.imagen_import = Leer_imagenes(os.path.join(basedir, "Assets", "image_arrow_up.png"))
        self.imagen_export=Leer_imagenes(os.path.join(basedir, "Assets", "file_save.png"))
        self.imagen_cancelar = Leer_imagenes(os.path.join(basedir, "Assets", "close.png"), (30, 30))
        self.imagen_eliminar = Leer_imagenes(os.path.join(basedir, "Assets", "delete.png"))
        self.imagen_ejecutar_modelo = Leer_imagenes(os.path.join(basedir, "Assets", "network_intelligence.png"))
        self.imagen_buscar_bd=Leer_imagenes(os.path.join(basedir,"Assets","search.png"),(16, 16))
        self.imagen_update_modelo = Leer_imagenes(os.path.join(basedir, "Assets", "network_intelligence_update.png"), (15, 15))
        self.imagen_admin = Leer_imagenes(os.path.join(basedir, "Assets", "admin.png"), (30, 30))
        self.imagen_principal = Leer_imagenes(os.path.join(basedir, "Assets", "medicalomni3d.png"), (70, 70))
        self.imagen_icono_monstrar=Leer_imagenes(os.path.join(basedir, "Assets", "visibility.png"),(12,13))

    def Frame_menu_deslizable(self):
        self.frame_banner = ttk.Frame(self, style="Banner.TFrame")
        self.frame_page = ttk.Frame(self, style="Page.TFrame")
        self.frame_menu = ttk.Frame(self, style="Menu_deslizable.TFrame")

        self.frame_banner.pack(side=tk.TOP, fill=tk.X)
        self.frame_menu.pack(side=tk.LEFT, fill=tk.Y, pady=3, padx=4)
        self.frame_page.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.frame_menu.pack_propagate(False)
        self.frame_banner.pack_propagate(False)
        self.frame_menu.configure(width=80)
        self.frame_banner.configure(height=70)
        self._overlay = tk.Frame(self.frame_page, bg="#C7C7C7")
        self._overlay.place_forget()

    def Frames_banco_imagenes(self):
        self.Ocultar_paginas()
        if hasattr(self, "frame_page_banco_imagenes"):
            self.frame_page_banco_imagenes.destroy()

        self.frame_page_banco_imagenes = ttk.Frame(
            self.frame_page,
            style="Page.TFrame"
        )
        self.frame_page_banco_imagenes.columnconfigure(0,weight=10)
        self.frame_page_banco_imagenes.columnconfigure(1, weight=0)
        self.frame_page_banco_imagenes.rowconfigure(0,weight=1)
        self.frame_page_banco_imagenes.rowconfigure(1, weight=1)
        self.frame_visualizador = ttk.Frame(self.frame_page_banco_imagenes,style="Menu_deslizable.TFrame")
        self.frame_configuracion_tabla = ttk.Frame(self.frame_page_banco_imagenes,style="Page_configuracion_banco.TFrame")
        self.frame_configuracion_tabla.columnconfigure(0,weight=1)
        self.frame_configuracion_tabla.rowconfigure(0, weight=1)
        self.frame_configuracion_tabla.rowconfigure(1, weight=10)
        self.frame_page_banco_imagenes.pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        self.frame_visualizador.grid(row=0,column=0,rowspan=2,sticky=tk.NSEW)
        self.frame_configuracion_tabla.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)
        self.Frames_banco_imagenes_tabla()
        self.visor = Visor_MedicalOmni3D(frame_visualizador=self.frame_visualizador)



    def Frames_banco_imagenes_tabla(self):
        self.frame_tabla = ttk.Frame(self.frame_configuracion_tabla, style="Page.TFrame")
        self.frame_configuracion_botones = ttk.Frame(self.frame_configuracion_tabla, style="Page.TFrame")
        self.frame_configuracion_botones.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
        self.frame_tabla.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
        self.frame_tabla.columnconfigure(0, weight=1)
        self.frame_tabla.rowconfigure(0, weight=1)
        self.tabla_banco=ttk.Treeview(self.frame_tabla,columns=self.columna_tabla,show="headings",cursor="hand2")
        self.tabla_banco.heading(column=0,text=self.columna_tabla[0],anchor=tk.CENTER)
        self.tabla_banco.heading(column=1, text=self.columna_tabla[1],anchor=tk.W)
        self.tabla_banco.heading(column=2, text=self.columna_tabla[2],anchor=tk.W)
        self.tabla_banco.column(column=0,width=40,anchor=tk.CENTER)
        self.tabla_banco.column(column=1, width=140, anchor=tk.CENTER)
        self.tabla_banco.column(column=2, width=60, anchor=tk.CENTER)
        self.tabla_banco.grid(row=0,column=0,sticky=tk.NSEW)
        scroll = ttk.Scrollbar(self.frame_tabla, orient=tk.VERTICAL, command=self.tabla_banco.yview, cursor="arrow")
        self.tabla_banco.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky=tk.NS)
        self.Cargar_imagenes()
        self.Frames_banco_botones()
        self.tabla_banco.bind(" <Double-1>", self.Visualizar_imagen)


    def Cargar_imagenes(self):
        try:
            lista = os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"])
            if lista:
                lista_2 = os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Salida_imagenes_modelo"])
                self.Eliminar_toda_tabla()
                self.lista_imagenes_tabla = []
                lista_codificar = []
                for indice, imagen in enumerate(lista, 1):
                    lista_nombres = os.path.basename(imagen).split(".", maxsplit=-2)
                    nombre_codificar = ".".join(lista_nombres[:3])
                    lista_codificar.append(nombre_codificar)
                    nombre = nombre_codificar.split(".")[0]
                    valor = True if nombre_codificar in lista_2 else False
                    self.lista_imagenes_tabla.append((indice, nombre, valor))
                self.imagenes_codificadas = Configuracionnnunetv2.Codificacion_imagenes(lista_imagenes_selecionadas=lista_codificar)
                lista.clear()
                self.importar_imagen()
            else:
                self.Eliminar_toda_tabla()

        except Exception as e:
            log.error(f"Error al cargar las imagenes a la tabla:\n{e}")

    def Eliminar_toda_tabla(self):
        try:
            if  not  self.lista_imagenes_tabla is None:
                for item in self.tabla_banco.get_children():
                    self.tabla_banco.delete(item)
                self.lista_imagenes_tabla=None
        except Exception as e:
            log.error(f"Error al eliminar la tabla:\n{e}")

    def Eliminar_imagen(self, evento):
        try:
            self.lista_imagenes_tabla=[]
            lista_imagenes=[]
            for item in self.tabla_banco.selection():
                imagen=".".join([self.tabla_banco.item(item)["values"][1],"nii.gz"])
                self.lista_imagenes_tabla.append(imagen)
                lista_imagenes.append(imagen.split(".")[-3])
            text=",".join(lista_imagenes)
            if  len(self.lista_imagenes_tabla )>0:
                respuesta=messagebox.askyesno(title="Eliminar imagen", message=f"Desea eliminar la imagen:\n{text}")
                if respuesta:
                    Configuracionnnunetv2.Eliminarcion(lista_imagenes_selecionadas=self.lista_imagenes_tabla,diccionario_paths=self.imagenes_codificadas)
                    for imagen_eliminar in self.lista_imagenes_tabla:

                        texto = f"{self.usuario.ACCIONES[4]}:{imagen_eliminar}".split(".")[0]
                        DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)

                    messagebox.showinfo(title="Eliminar imágenes",message=f"Se eliminaron correctamente las siguientes imágenes:\n{text}")
                    self.Cargar_imagenes()
            else:
                messagebox.showerror("Error Eliminar", "Por favor seleccione por lo menos una imagen.")
            self.frame_botones.focus()
        except Exception as e:
            log.error(f"Error al eliminar las imagenes:\n{e}")

    def Ocultar_paginas(self):

        if hasattr(self, "visor") and self.visor is not None:
            self.visor.destruir_visor()
            self.visor = None

        if hasattr(self, "frame_page_banco_imagenes"):
            self.frame_page_banco_imagenes.pack_forget()
        if hasattr(self, "frame_page_configuaracion"):
            self.frame_page_configuaracion.pack_forget()
        if hasattr(self, "frame_page_admin"):
            self.frame_page_admin.pack_forget()

        if hasattr(self, "notebook_admin"):
            self.notebook_admin.pack_forget()

    def  Visualizar_imagen(self,event):
        try:
            region = self.tabla_banco.identify_region(event.x, event.y)
            if self.tabla_banco.selection() and region == "cell":
                nombre_imagen = self.tabla_banco.item(self.tabla_banco.selection()[0])["values"][1]+".nii.gz"
                self.imagen_visor=self.imagenes_codificadas[nombre_imagen]["input_path"]
                Configuracionnnunetv2.Descifrar_imagenes(path_imagen=self.imagen_visor)
                self.visor.Cargar_nueva_imagen(imagen=self.imagen_visor)
                if nombre_imagen:
                    if "rojo" not in self.tabla_banco.item(self.tabla_banco.selection()[0])['tags'][0]:
                        self.mascara=self.imagenes_codificadas[nombre_imagen]["file_delete"]
                        self.visor.inicializar_vtk_seguro(mascara= self.mascara)
                    else:
                        self.visor.inicializar_vtk_seguro()
                os.remove(self.imagen_visor)

        except Exception as e:
            log.error(f"Error en la visualizacion de la imagen seleccionada:\n{e}")

    def Cargar_modelos(self):
        try:
            if os.path.exists(self.archivojson):
                self.eleccion_modelos = [modelos for modelos in self.configuracion_sistema["modelos"].keys() if
                                         modelos != ""]
                if len(self.eleccion_modelos) > 0:
                    self.boton_selecion_modelo.config(values=self.eleccion_modelos)
                    if self.configuracion_sistema["modelo_seleccionado"]!="":
                        self.boton_selecion_modelo.set(self.configuracion_sistema["modelo_seleccionado"])
                    else:
                        self.boton_selecion_modelo.current(0)
                        self.Seleccion_modelos(event=None)

                else:

                    self.boton_selecion_modelo.set("Importar modelo")

            else:
                log.error("Error no se pudo encontrar  el archivo json de la aplicacion")
        except Exception as e :
           log.error(f"Error al cargar los modelos:\n{e}")

    def Seleccion_modelos(self,event):
        if os.path.exists(self.archivojson):
            mode=self.boton_selecion_modelo.get()
            self.configuracion_sistema["modelo_seleccionado"]=mode
            with open(self.archivojson, "w") as f:
                json.dump(self.configuracion_sistema, f, indent=4)


    def Ejecutar_modelo(self, evento):
        try:
            lista_imagenes = self.tabla_banco.selection()
            self.lista_imagenes_tabla = []
            modelo_seleccionado = self.boton_selecion_modelo.get()
            if lista_imagenes:
                if modelo_seleccionado != "Importar modelo":
                    for item in lista_imagenes:
                        imagen = ".".join([self.tabla_banco.item(item)["values"][1], "nii.gz"])
                        self.lista_imagenes_tabla.append(imagen)
                    text = ",".join(self.lista_imagenes_tabla)
                    respuesta = messagebox.askyesno(title="Ejecutando Inferencia",message=f"Desea ejecutar la inferencia de la imagen:\n{text}")
                    if respuesta:
                        self.imagenes_codificadas = Configuracionnnunetv2.Codificacion_imagenes(lista_imagenes_selecionadas=self.lista_imagenes_tabla)
                        for imagen in self.lista_imagenes_tabla:
                            Configuracionnnunetv2.Descifrar_imagenes(self.imagenes_codificadas[imagen]['input_path'])
                        with open(self.archivojson, "r") as archivojson:
                            self.configuracion_sistema = json.load(archivojson)
                        Espaciado = Configuracionnnunetv2.Obtener_espaciado_original(lista_imagenes_selecionadas=self.lista_imagenes_tabla)
                        VentanaCargaSubproceso(master=self,usuario=self.usuario,lista_imagenes_tabla=self.lista_imagenes_tabla,imagenes_codificadas=self.imagenes_codificadas,espaciado_orig=Espaciado,congiguracion=self.configuracion_sistema,callback=self.Cargar_imagenes)
                else:
                    messagebox.showerror("Error Inferencia","Por favor seleccione un modelo.")
            else:
                messagebox.showerror("Error Inferencia", "Por favor seleccione por lo menos una imagen.")
            self.frame_botones.focus()
        except Exception as e:
            log.error(f"Error en la ejecucion de la inferencia:\n{e}")

    def Cargar_extension(self,evento):
        try:
            if os.path.exists(self.archivojson):
                self.configuracion_sistema["tipo_archivo_ex"] =self.variable_extension.get()
                with open(self.archivojson, "w") as f:
                    json.dump(self.configuracion_sistema, f, indent=4)
        except Exception as e:
            log.error(f"Error en la carga de la extension de la imagenes:\n{e}")
    def Frames_banco_botones(self):
        self.frame_botones=ttk.Frame(self.frame_configuracion_botones,style="Page_botones.TFrame")
        self.frame_botones.rowconfigure(0,weight=1)
        self.frame_botones.rowconfigure(1, weight=1)
        self.frame_botones.columnconfigure(0, weight=1)
        self.frame_botones.columnconfigure(1, weight=1)
        self.frame_botones.columnconfigure(2, weight=1)
        self.boton_importar=ttk.Button(self.frame_botones, text="Importar Imagen", image=self.imagen_import, compound=tk.LEFT, cursor="hand2", command=lambda :self.Almacenamiento_imagenes(evento=None))
        self.boton_export = ttk.Button(self.frame_botones, text="Exportar Imagen", image=self.imagen_export, compound=tk.LEFT,cursor="hand2",command=lambda :self.exportar_imagen(evento=None))
        self.boton_eliminar = ttk.Button(self.frame_botones, text="Eliminar Imagen", image=self.imagen_eliminar, compound=tk.LEFT, cursor="hand2",command=lambda :self.Eliminar_imagen(evento=None))
        self.boton_selecion_modelo=ttk.Combobox(self.frame_botones, values=self.eleccion_modelos, state="readonly", width=22, font=(" ", 9), justify="center", height=5, cursor="hand2")
        self.boton_inferencia = ttk.Button(self.frame_botones, text="Ejecutar modelo", image=self.imagen_ejecutar_modelo, compound=tk.LEFT, cursor="hand2",command=lambda :self.Ejecutar_modelo(evento=None))
        self.frame_botones.pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        self.boton_importar.grid(row=0,column=0,pady=1,padx=5)
        self.boton_export.grid(row=0,column=1,sticky=tk.W,pady=5,padx=5)
        self.boton_eliminar.grid(row=1,column=0,pady=1,padx=5)
        self.boton_selecion_modelo.grid(row=1,column=1,pady=5)
        self.boton_inferencia.grid(row=1,column=2,pady=1,padx=5,sticky=tk.W)
        self.boton_importar.bind("<Return>", self.Almacenamiento_imagenes)
        self.boton_export.bind("<Return>", self.exportar_imagen)
        self.boton_eliminar.bind("<Return>", self.Eliminar_imagen)
        self.boton_inferencia.bind("<Return>", self.Ejecutar_modelo)
        self.boton_selecion_modelo.bind("<<ComboboxSelected>>", self.Seleccion_modelos)
        self.Cargar_modelos()
        self.botones_exportacion_imagenes()

    def botones_exportacion_imagenes(self):

        if self.configuracion_sistema is None:
            try:
                with open(self.archivojson, "r") as f:
                    self.configuracion_sistema = json.load(f)
            except Exception as e:
                log.error(f"Error al recargar configuración en botones_exportacion: {e}")
                return

        self.frame_botones_extesion = ttk.Frame(self.frame_botones, style="Page.TFrame")
        self.frame_botones_extesion.grid(row=0, column=2, sticky=tk.EW, padx=5, pady=5)
        self.variable_extension = tk.StringVar(
            value=self.configuracion_sistema.get("tipo_archivo_ex", "")  # ✅ .get() con fallback
        )
        for i, extension in enumerate(Configuracionnnunetv2.TIPO_EXTENSION.keys()):
            fila = i // 2
            columna = i % 2
            boton = ttk.Radiobutton(
                self.frame_botones_extesion,
                text=extension,
                variable=self.variable_extension,
                value=extension,
                cursor="hand2",
                command=lambda: self.Cargar_extension(evento=None)
            )
            boton.bind("<space>", self.Cargar_extension)
            boton.bind("<Return>", self.Cargar_extension)
            boton.grid(row=fila, column=columna, padx=2, pady=2, sticky="w")

    def exportar_imagen(self,evento):
        try:
            if self.configuracion_sistema["path_export_imagen"]!="":
                with open(self.archivojson, "r") as archivojson:
                    self.configuracion_sistema=json.load(archivojson)
                initialdir = self.configuracion_sistema["path_export_imagen"]
            else:
                initialdir = os.path.expanduser("~")

            ruta = filedialog.askdirectory(title="Seleccione la carpeta para exportar las mascaras",initialdir=initialdir)
            if ruta:
                self.lista_imagenes_tabla = []
                self.configuracion_sistema["path_export_imagen"] = ruta
                with open(self.archivojson, "w") as f:
                    json.dump(self.configuracion_sistema, f, indent=4)
                for item in self.tabla_banco.selection():
                    imagen = ".".join([self.tabla_banco.item(item)["values"][1], "nii.gz"])
                    self.lista_imagenes_tabla.append(imagen)
                if len(self.lista_imagenes_tabla) > 0:
                        Configuracionnnunetv2.Exportacion_imagenes(tipo_extension=self.variable_extension.get(),lista_imagenes_selecionadas=self.lista_imagenes_tabla,path_exportacion=ruta,diccionario_paths=self.imagenes_codificadas)
                        for imagen in self.lista_imagenes_tabla:
                            texto = f"{self.usuario.ACCIONES[5]}:{imagen}"
                            DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
                else:
                    messagebox.showerror("Error Exportación", "Por favor seleccione por lo menos una imagen.")
            self.frame_botones.focus()

        except Exception as e :
            log.error(f"Error al exportar las imagenes:\n{e}")

    def importar_imagen(self):
        try:
            if self.lista_imagenes_tabla is not None:
                for dato in self.lista_imagenes_tabla:
                    indicador = "⬤"
                    item = self.tabla_banco.insert("",tk.END,values=(dato[0], dato[1], indicador))
                    if dato[2]:
                        self.tabla_banco.tag_configure(f"verde_{item}",foreground="green")
                        self.tabla_banco.item(item, tags=(f"verde_{item}",))
                    else:
                        self.tabla_banco.tag_configure(f"rojo_{item}",foreground="red")
                        self.tabla_banco.item(item, tags=(f"rojo_{item}",))

        except Exception as e:
            log.error(f"Error al insertar los datos de las imagenes en la tabla:\n{e}")

    def Pagina_configuracion(self):
        self.Ocultar_paginas()
        if not hasattr(self, "frame_page_configuaracion"):
            self.frame_page_configuaracion = ttk.Frame(self.frame_page,style="Menu_deslizable.TFrame")
        self.frame_page_configuaracion.pack(fill=tk.BOTH,expand=True,pady=5)
        self.frame_importacion_modelo()

    def importar_modelo(self,event):
        try:
            if self.configuracion_sistema["path_import_modelo"] !="":
                with open(self.archivojson, "r") as archivojson:
                    self.configuracion_sistema=json.load(archivojson)
                initialdir=self.configuracion_sistema["path_import_modelo"]
            else:
                initialdir = os.path.expanduser("~")

            ruta=filedialog.askopenfile(title="Seleccione el modelo para importar",initialdir=initialdir,filetypes=[("Archivos ZIP", "*.zip")])
            if ruta:
                Configuracionnnunetv2.ventana_importar_modelo(master=self, path_model=ruta.name,callback=self.actualizar_modelos)
                self.configuracion_sistema["path_import_modelo"] = os.path.dirname(ruta.name)
                with open(self.archivojson, "w") as f:
                    json.dump(self.configuracion_sistema, f, indent=4)
            print(self.configuracion_sistema,"ventana principal")
            self.frame_immportacion_modelo.focus()
        except Exception as e:
            log.error(f"Error al importar modelo:\n{e}")

    def actualizar_modelos(self):
        try:
            with open(self.archivojson, "r") as f:
                self.configuracion_sistema = json.load(f)
            print(self.configuracion_sistema)
        except Exception as e:
            log.error(f"Error al recargar configuración tras importar modelo: {e}")
            return
        self.Cargar_modelos()

        if self.eleccion_modelos and len(self.eleccion_modelos) > 0:
            self.boton_modelos_configuracion.config(values=self.eleccion_modelos)
            modelo_actual = self.configuracion_sistema.get("modelo_seleccionado", "")
            if modelo_actual != "" and modelo_actual in self.eleccion_modelos:
                self.boton_modelos_configuracion.set(modelo_actual)
            else:
                self.boton_modelos_configuracion.current(0)
                self.Seleccion_modelos(event=None)

    def guardar_configuracion_sistema(self,event):
        respuesta = messagebox.askyesno(title="Guardar configuración del sistema",message="¿Desea guardar los cambios realizados en la configuración del sistema?")
        if respuesta:
            if self.boton_modelos_configuracion.get()!= "Importar modelo":
                self.configuracion_sistema["modelos"][self.boton_modelos_configuracion.get()]["Normalizacion"] = self.normalizacion.get()
                self.configuracion_sistema["modelos"][self.boton_modelos_configuracion.get()]["Espaciado"] = self.espaciado.get()
                self.configuracion_sistema["modelos"][self.boton_modelos_configuracion.get()]["device"] = self.boton_dispositivo_configuracion.get()
                self.configuracion_sistema["modelos"][self.boton_modelos_configuracion.get()]["nuevo_espaciado"] = [int(self.entry_x.get()), int(self.entry_y.get()), int(self.entry_z.get())]
                self.dispositivo_selecionado=self.boton_dispositivo_configuracion.get()
                self.lista_espaciado=[int(self.entry_x.get()), int(self.entry_y.get()), int(self.entry_z.get())]
                nombre_imagen = self.boton_modelos_configuracion.get()
                texto = f"{self.usuario.ACCIONES[10]}: modelo {nombre_imagen}"
                DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
                messagebox.showinfo(title="Configuración guardada",message="Los cambios en la configuración del sistema se han guardado correctamente.")
                with open(self.archivojson, "w") as f:
                    json.dump(self.configuracion_sistema, f, indent=4)
                self.configuracion_sistema=Configuracionnnunetv2.Configuracion_apcivmapcas_json()
            else:
                messagebox.showerror(title="Error al guardar la configuración",message="No se guardaron los cambios. Importe un modelo válido.")
        self.frame_immportacion_modelo.focus()
    def cargar_configuracion(self,even):
        modelo=self.boton_modelos_configuracion.get()
        self.normalizacion.set(value=self.configuracion_sistema["modelos"][modelo]["Normalizacion"])
        self.espaciado.set(value=self.configuracion_sistema["modelos"][modelo]["Espaciado"])
        self.lista_espaciado=self.configuracion_sistema["modelos"][modelo]["nuevo_espaciado"]
        self.entry_x.delete(0,tk.END)
        self.entry_y.delete(0, tk.END)
        self.entry_z.delete(0, tk.END)
        self.entry_x.insert(0,str(self.lista_espaciado[0]))
        self.entry_y.insert(0,str(self.lista_espaciado[1]))
        self.entry_z.insert(0,str(self.lista_espaciado[2]))
        self.boton_dispositivo_configuracion.set(value=self.configuracion_sistema["modelos"][modelo]["device"])


    def frame_importacion_modelo(self):
        self.frame_immportacion_modelo = ttk.Frame(self.frame_page_configuaracion,style="Admin.TFrame")
        self.frame_page_configuaracion.columnconfigure(0, weight=1)
        self.frame_page_configuaracion.rowconfigure(0, weight=1)
        ttk.Label(self.frame_immportacion_modelo,style="Banner.TLabel",text="Configuración de Modelos",font=(" ", 14, "bold")).pack(anchor="w", padx=15, pady=10)
        frame_modelos = ttk.LabelFrame(self.frame_immportacion_modelo, text="Gestión de Modelos")
        frame_modelos.pack(fill=tk.X, padx=30, pady=10)
        frame_pre = ttk.LabelFrame(self.frame_immportacion_modelo, text="Preprocesamiento")
        frame_pre.pack(fill=tk.X, padx=30, pady=10)
        ttk.Label(frame_modelos,text="Modelo seleccionado:",style="Config.TLabel").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(frame_modelos, text="Dispositivo de ejecución:", style="Config.TLabel").grid(row=0, column=2, padx=10,pady=10)
        self.boton_modelos_configuracion = ttk.Combobox(frame_modelos, values=self.eleccion_modelos, state="readonly", width=25, cursor="hand2")
        self.boton_dispositivo_configuracion = ttk.Combobox(frame_modelos, values=self.dispositivo, state="readonly", width=10, cursor="hand2")
        self.boton_dispositivo_configuracion.set(self.dispositivo_selecionado)
        self.boton_modelos_configuracion.bind("<<ComboboxSelected>>", self.cargar_configuracion)
        boton_importar_modelo=ttk.Button(frame_modelos,text="Importar Modelo",image=self.imagen_update_modelo,cursor="hand2",command=lambda :self.importar_modelo(event=None),compound=tk.LEFT)
        boton_importar_modelo.bind("<Return>",self.importar_modelo)
        boton_eliminar=ttk.Button(frame_modelos,text="Eliminar Modelo",cursor="hand2",command=lambda :self.Eliminar_modelo(event=None))
        boton_eliminar.bind("<Return>",self.Eliminar_modelo)
        self.boton_normalizacion = ttk.Checkbutton(frame_pre, text="Aplicar normalización", variable=self.normalizacion,cursor="hand2")
        self.boton_espaciado = ttk.Checkbutton(frame_pre, text="Aplicar cambio de espaciado", variable=self.espaciado,cursor="hand2")
        boton_eliminar.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.boton_modelos_configuracion.grid(row=0, column=1, padx=10, pady=10)
        self.boton_dispositivo_configuracion.grid(row=0, column=3, padx=10, pady=10)
        boton_importar_modelo.grid(row=1, column=0, padx=10, pady=10,sticky=tk.W)
        self.boton_espaciado.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.boton_normalizacion.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        boton_guardar=ttk.Button(self.frame_immportacion_modelo,text="Guardar configuración",command=lambda :self.guardar_configuracion_sistema(event=None))
        boton_guardar.bind("<Return>",self.guardar_configuracion_sistema)
        self.entry_x = ttk.Entry(frame_pre, width=10,justify=tk.CENTER)
        self.entry_y = ttk.Entry(frame_pre, width=10,justify=tk.CENTER)
        self.entry_z = ttk.Entry(frame_pre, width=10,justify=tk.CENTER)
        boton_guardar.pack(anchor="e", padx=15, pady=15)
        ttk.Label(frame_pre, text="X",style="Config.TLabel",cursor="hand2").grid(row=2, column=1)
        ttk.Label(frame_pre, text="Y",style="Config.TLabel",cursor="hand2",justify=tk.CENTER).grid(row=2, column=2)
        ttk.Label(frame_pre, text="Z",style="Config.TLabel",cursor="hand2",justify=tk.CENTER).grid(row=2, column=3)
        self.entry_x.insert(0, string=str(self.lista_espaciado[0]))
        self.entry_y.insert(0, string=str(self.lista_espaciado[1]))
        self.entry_z.insert(0, string=str(self.lista_espaciado[2]))
        self.entry_x.grid(row=3, column=1, padx=10, pady=5)
        self.entry_y.grid(row=3, column=2, padx=10, pady=5)
        self.entry_z.grid(row=3, column=3, padx=10, pady=5)
        self.frame_immportacion_modelo.grid(row=0, column=0, padx=260, pady=160, sticky=tk.NSEW)
        if self.eleccion_modelos:
            if self.configuracion_sistema["modelo_seleccionado"] != "":
                self.boton_modelos_configuracion.set(self.configuracion_sistema["modelo_seleccionado"])
                self.cargar_configuracion(even=None)
            else:
                self.boton_modelos_configuracion.current(0)
        else:
            self.boton_modelos_configuracion.set("Importar modelo")

    def Eliminar_modelo(self,event):
        if self.boton_modelos_configuracion.get()!="Importar modelo":
            Configuracionnnunetv2.Desinstalar_modelos(self.boton_modelos_configuracion.get())
            with open(self.archivojson, "r") as archivo:
                self.configuracion_sistema= json.load(archivo)
            respuesta = messagebox.askyesno(title="Eliminar modelo",message=f"¿Está seguro de que desea eliminar el modelo '{self.boton_modelos_configuracion.get()}'?")
            if respuesta:
                self.eleccion_modelos.remove(self.boton_modelos_configuracion.get())
                if self.eleccion_modelos:
                    self.boton_modelos_configuracion.config(values=self.eleccion_modelos)
                    self.boton_modelos_configuracion.current(0)
                    self.cargar_configuracion(even=None)
                else:
                    self.boton_modelos_configuracion.set("Importar modelo")
                messagebox.showinfo(title="Éxito al eliminar el modelo", message="El modelo se eliminó correctamente.")
        else:
            messagebox.showerror(title="Error al eliminar el modelo",message="No hay un modelo válido para eliminar.")

    def Pagina_admin(self):
        self.Ocultar_paginas()
        if not hasattr(self, "frame_page_admin"):
            self.frame_page_admin = ttk.Frame(self.frame_page)
        if not hasattr(self, "notebook_admin"):
            self.notebook_admin = ttk.Notebook(self.frame_page_admin)
            self.gestion_usuarios()
            self.gestion_log()
            self.tab_usuarios.focus()
        self.frame_page_admin.pack(fill=tk.BOTH, expand=True)
        self.notebook_admin.pack(fill="both", expand=True)

        self.notebook_admin.bind("<<NotebookTabChanged>>", self.cambio_pestana)
    def Cargar_datos_usuarios(self):
        if  self.lista_usuarios is None:
            self.lista_usuarios = DAOMedicalOmni3D.Seleccion_usuarios()
            self.list_logs_usuarios = []
            for usuario in self.lista_usuarios:
                self.tabla_usuarios.insert(parent="", index=tk.END, values=(usuario.id_usuario,usuario.username,usuario.rol,"Bloqueado"if usuario.bloqueado!=0 else"Desbloqueado",usuario.fecha))


    def frame_tabla_usuarios(self):
        self.frame_tabla_usuario = ttk.Frame(self.frame_gestion_usuarios, style="Banner.TFrame")
        self.frame_tabla_usuario.columnconfigure(0, weight=1)
        self.frame_tabla_usuario.rowconfigure(0, weight=10)
        self.frame_tabla_usuario.rowconfigure(1, weight=0)
        self.tabla_usuarios = ttk.Treeview(self.frame_tabla_usuario, columns=self.columna_tabla_usuario,show="headings", cursor="hand2")
        self.tabla_usuarios.heading(column=0, text=self.columna_tabla_usuario[0], anchor=tk.CENTER)
        self.tabla_usuarios.heading(column=1, text=self.columna_tabla_usuario[1], anchor=tk.W)
        self.tabla_usuarios.heading(column=2, text=self.columna_tabla_usuario[2], anchor=tk.W)
        self.tabla_usuarios.heading(column=3, text=self.columna_tabla_usuario[3], anchor=tk.W)
        self.tabla_usuarios.heading(column=4, text=self.columna_tabla_usuario[4], anchor=tk.W)
        self.tabla_usuarios.column(column=0, width=40, anchor=tk.CENTER)
        self.tabla_usuarios.column(column=1, width=140, anchor=tk.CENTER)
        self.tabla_usuarios.column(column=2, width=60, anchor=tk.CENTER)
        self.tabla_usuarios.column(column=3, width=60, anchor=tk.CENTER)
        self.tabla_usuarios.column(column=4, width=60, anchor=tk.CENTER)
        self.tabla_usuarios.grid(row=0, column=0, sticky=tk.NSEW)
        scroll = ttk.Scrollbar(self.frame_tabla_usuario, orient=tk.VERTICAL, command=self.tabla_usuarios.yview,cursor="arrow")
        self.tabla_usuarios.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky=tk.NS)
        self.frame_tabla_usuario.grid(row=1, column=0, columnspan=2, padx=200, sticky=tk.NSEW)
        ttk.Separator(self.frame_gestion_usuarios, orient="horizontal").grid(row=2, column=0, columnspan=2,sticky=tk.EW, pady=25)
        self.Cargar_datos_usuarios()

    def Buscar_usuarios(self,evento):
        if self.buscador.get()!="":
            self.Eliminar_toda_tabla_usuarios()
            if self.lista_usuarios is None:
                self.lista_usuarios = DAOMedicalOmni3D.Seleccion_usuarios_buscar(texto=self.buscador.get())
                for usuario in self.lista_usuarios:
                    self.tabla_usuarios.insert(parent="", index=tk.END,values=(usuario.id_usuario, usuario.username, usuario.rol,"Bloqueado" if usuario.bloqueado != 0 else "Desbloqueado",usuario.fecha))
        else:
            self.Eliminar_toda_tabla_usuarios()
            self.Cargar_datos_usuarios()

    def Eliminar_usuario(self,event):
        lista_usuarios=self.tabla_usuarios.selection()
        if lista_usuarios:
            if not (len(self.tabla_usuarios.get_children())==1 and self.tabla_usuarios.item(self.tabla_usuarios.selection()[0])['values'][2] == "Administrador"):
                usuario=Usuario(id_usuario=self.tabla_usuarios.item(lista_usuarios[0])['values'][0],username=self.tabla_usuarios.item(lista_usuarios[0])['values'][1])
                respuesta = messagebox.askyesno(title="Eliminar usuario",message=f"¿Está seguro de que desea eliminar el siguiente usuario?\n\nUsuario: {usuario.username}")
                if respuesta:
                    verificador = DAOMedicalOmni3D.Eliminar_usuario(user=usuario)
                    if verificador:
                        self.tabla_usuarios.delete(lista_usuarios[0])
                        texto = f"{self.usuario.ACCIONES[9]}: {usuario.username}"
                        DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
                        messagebox.showinfo("Exito eliminar usuario", f"Sea eliminado al usuario de manera exitosa.")
                        self.frame_page_admin.focus()
                    else:
                        messagebox.showerror("Error eliminar usuario", f"No sea podido eliminar al usuario.")
            else:
                messagebox.showerror(title="Eliminar usuario",message="No es posible eliminar el último administrador del sistema.")
        else:
            messagebox.showerror("Error en eliminar usuario", "Por favor seleccione por lo menos un usuario.")

        self.frame_page_admin.focus()

    def frame_botones_usuarios_gestion(self):
        self.frame_botones_usuarios = ttk.Frame(self.frame_tabla_usuario, style="Page_uausarios_banco.TFrame")
        self.frame_botones_usuarios.grid(row=1,column=0,columnspan=1,padx=20,pady=20)
        self.frame_botones_usuarios.columnconfigure(0, weight=1)
        self.frame_botones_usuarios.columnconfigure(1, weight=1)
        self.frame_botones_usuarios.columnconfigure(2, weight=1)
        self.boton_agregar_usuario=ttk.Button(self.frame_botones_usuarios, text="Nuevo usuario", command=lambda :self.Ventana_creacion_usuario(event=None))
        self.boton_agregar_usuario.bind("<Return>", self.Ventana_creacion_usuario)
        self.boton_editar_usuario = ttk.Button(self.frame_botones_usuarios, text="Editar usuario",command=lambda :self.Editar_usuario(event=None))
        self.boton_editar_usuario.bind("<Return>", self.Editar_usuario)
        self.boton_eliminar_usuario = ttk.Button(self.frame_botones_usuarios, text="Eliminar usuario",command=lambda : self.Eliminar_usuario(event=None))
        self.boton_eliminar_usuario.bind("<Return>", self.Eliminar_usuario)
        self.boton_agregar_usuario.grid(row=1,column=0,sticky=tk.EW,padx=20,pady=8)
        self.boton_editar_usuario.grid(row=1, column=1, sticky=tk.EW,padx=20,pady=8)
        self.boton_eliminar_usuario.grid(row=1, column=2, sticky=tk.EW,padx=20,pady=8)

    def gestion_usuarios(self):
        self.tab_usuarios = ttk.Frame(self.notebook_admin,style="Menu_deslizable.TFrame")
        self.tab_usuarios.columnconfigure(0,weight=1)
        self.tab_usuarios.rowconfigure(0, weight=1)
        self.tab_usuarios.rowconfigure(1, weight=100)
        self.notebook_admin.add(self.tab_usuarios, text="Usuarios")
        ttk.Label(self.tab_usuarios, style="Menu_deslizable.TLabel",text="Gestión de usuarios",font=(" ", 20, "bold")).grid(row=0,column=0,padx=20,pady=5,sticky=tk.W)
        self.frame_gestion_usuarios=ttk.Frame(self.tab_usuarios,style="Admin.TFrame")
        self.frame_gestion_usuarios.columnconfigure(0, weight=1)
        self.frame_gestion_usuarios.rowconfigure(1, weight=20)
        self.frame_gestion_usuarios.rowconfigure(2, weight=20)
        self.frame_buscador=ttk.Frame(self.frame_gestion_usuarios,style="Banner.TFrame")
        tk.Label(self.frame_buscador,text="Buscar:",bg="#071640",foreground="white",font=(" ", 12, " ")).grid(row=0,column=0,sticky=tk.W,pady=5)
        self.buscador=ttk.Entry(self.frame_buscador,width=30,font=(" ", 12, " "))
        self.boton_buscador=ttk.Button(self.frame_buscador,image=self.imagen_buscar_bd,cursor="hand2",command=lambda :self.Buscar_usuarios(evento=None))
        self.boton_buscador.bind("<Return>", self.Buscar_usuarios)
        self.buscador.bind("<Return>", self.Buscar_usuarios)
        self.buscador.grid(row=0,column=1,sticky=tk.W,pady=5)
        self.boton_buscador.grid(row=0, column=2,sticky=tk.W)
        self.frame_tabla_usuarios()
        self.frame_buscador.grid(row=0,column=0,pady=20,padx=10,sticky=tk.W)
        self.frame_gestion_usuarios.grid(row=1,column=0,sticky=tk.NSEW,padx=100,pady=20)
        self.frame_botones_usuarios_gestion()


    def Mostrar_ocultar_password(self,event):
        if self.mostrar_crear:
            self.mostrar_crear=False
            self.imagen_icono_monstrar=Leer_imagenes(os.path.join(basedir, "Assets", "visibility_off.png"), (12,13))
            self.contrasena_nuevo_usuario_mostar.configure(image=self.imagen_icono_monstrar)
            self.contrasena_nuevo_usuario.configure(show="")
        else:
            self.mostrar_crear = True
            self.imagen_icono_monstrar=Leer_imagenes(os.path.join(basedir, "Assets", "visibility.png"), (12,13))
            self.contrasena_nuevo_usuario_mostar.configure(image=self.imagen_icono_monstrar)
            self.contrasena_nuevo_usuario.configure(show="●")

    def Guardar_usuario_editado(self,event):
        if re.match(self.email_pattern,self.correo_editar_usuario.get().lower()):
            respuesta=False
            if self.cambiar_password.get():
                if re.match(self.password_pattern,self.contrasena_editar_usuario.get()):
                    self.usuario_editar.username = self.correo_editar_usuario.get()
                    self.usuario_editar.password=self.contrasena_editar_usuario.get()
                    self.usuario_editar.rol=self.Rol_editar_usuario.get()
                    self.usuario_editar.bloqueado=self.Estado_editar_usuario.get()
                    respuesta = messagebox.askyesno(
                        title="Nuevo usuario",message=(
                            f"¿Está seguro de que desea actualizar la siguiente información?\n"
                            f"-Correo: {self.usuario_editar.username}\n"
                            f"-Contraseña: {self.usuario_editar.password}\n"
                            f"-Rol: {self.usuario_editar.rol}\n"
                            f"-Estado: {self.usuario_editar.bloqueado}"))
                else:
                    messagebox.showerror(title="Contraseña inválida",message="La contraseña debe tener al menos 8 caracteres, una letra mayúscula y un número o carácter especial.")
            else:
                self.usuario_editar.username = self.correo_editar_usuario.get()
                self.usuario_editar.rol = self.Rol_editar_usuario.get()
                self.usuario_editar.bloqueado = self.Estado_editar_usuario.get()
                respuesta = messagebox.askyesno(title="Nuevo usuario",message=(
                        f"¿Está seguro de que desea actualizar la siguiente información?\n"
                        f"-Correo: {self.usuario_editar.username}\n"
                        f"-Rol: {self.usuario_editar.rol}\n"
                        f"-Estado: {self.usuario_editar.bloqueado}"))
            if respuesta:
                if self.Estado_editar_usuario.get() != "Desbloqueado":
                    self.usuario_editar.bloqueado = 1
                else:
                    self.usuario_editar.bloqueado = 0

                if self.cambiar_password.get():
                    verificador = DAOMedicalOmni3D.Editar_usuario_password(user=self.usuario_editar)
                    self.Eliminar_toda_tabla_usuarios()
                    self.Cargar_datos_usuarios()
                    self.ventana_editar.destroy()
                else:
                    verificador = DAOMedicalOmni3D.Editar_usuario(user=self.usuario_editar)
                if verificador:
                    texto = f"{self.usuario.ACCIONES[8]}: {self.usuario_editar.username}"
                    DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
                    self.Eliminar_toda_tabla_usuarios()
                    self.Cargar_datos_usuarios()
                    self.ventana_editar.destroy()
        else:
            messagebox.showerror(title="Correo inválido",message="Ingrese un correo electrónico válido.")

    def Editar_usuario(self,event):
        if self.tabla_usuarios.selection():
            lista_usuario=self.tabla_usuarios.item(self.tabla_usuarios.selection()[0])['values']
            self.usuario_editar=Usuario(id_usuario=lista_usuario[0],username=lista_usuario[1],rol=lista_usuario[2],bloqueado=lista_usuario[3],fecha=lista_usuario[4])
            if self.usuario_editar:
                self.Ventana_editar_usuario()
        else:
            messagebox.showerror("Error en editar usuario", "Por favor seleccione por lo menos un usuario.")
        self.frame_page_admin.focus()
    def Guardar_usuario(self,event):
        if re.match(self.email_pattern,self.correo_nuevo_usuario.get().lower()):
            if re.match(self.password_pattern,self.contrasena_nuevo_usuario.get()):
                usuario_nuevo = Usuario(username=self.correo_nuevo_usuario.get().lower(), password=self.contrasena_nuevo_usuario.get(),rol=self.Rol_nuevo_usuario.get(), bloqueado=self.Estado_nuevo_usuario.get())
                respuesta = messagebox.askyesno(
                    title="Nuevo usuario",
                    message=(
                        f"¿Está seguro de que desea guardar el siguiente usuario?\n"
                        f"-Correo: {usuario_nuevo.username}\n"
                        f"-Contraseña: {usuario_nuevo.password}\n"
                        f"-Rol: {usuario_nuevo.rol}\n"
                        f"-Estado: {usuario_nuevo.bloqueado}"))
                if respuesta:
                    if self.Estado_nuevo_usuario.get() != "Desbloqueado":
                        usuario_nuevo.bloqueado = 1
                    else:
                        usuario_nuevo.bloqueado = 0
                    verificador=DAOMedicalOmni3D.Insertar_usuario(user=usuario_nuevo)
                    if verificador:
                        texto = f"{self.usuario.ACCIONES[7]}: {usuario_nuevo.username}"
                        DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
                        self.Eliminar_toda_tabla_usuarios()
                        self.Cargar_datos_usuarios()
                        self.ventana.destroy()
            else:
                messagebox.showerror(title="Contraseña inválida", message="La contraseña debe tener al menos 8 caracteres, una letra mayúscula y un número o carácter especial.")
        else:
            messagebox.showerror(title="Correo inválido",message="Ingrese un correo electrónico válido.")

    def Eliminar_toda_tabla_usuarios(self):
        if self.lista_usuarios is not None:
            for item in self.tabla_usuarios.get_children():
                self.tabla_usuarios.delete(item)
            self.lista_usuarios=None
    def Eliminar_toda_tabla_logs(self):
        if self.lista_logs is not None:
            for item in self.tabla_logs.get_children():
                self.tabla_logs.delete(item)
            self.lista_logs=None
    def habilitar_password(self):
        if self.cambiar_password.get():
            self.contrasena_editar_usuario.config(state=tk.NORMAL)
        else:
            self.contrasena_editar_usuario.delete(0, tk.END)
            self.contrasena_editar_usuario.config(state=tk.DISABLED)

    def Mostrar_ocultar_password_editar(self,event):
        if self.mostrar_editar:
            self.mostrar_editar = False
            self.imagen_icono_monstrar = Leer_imagenes(os.path.join(basedir, "Assets", "visibility_off.png"), (12, 13))
            self.contrasena_editar_usuario_mostar.configure(image=self.imagen_icono_monstrar)
            self.contrasena_editar_usuario.configure(show="")
        else:
            self.mostrar_editar = True
            self.imagen_icono_monstrar = Leer_imagenes(os.path.join(basedir, "Assets", "visibility.png"), (12, 13))
            self.contrasena_editar_usuario_mostar.configure(image=self.imagen_icono_monstrar)
            self.contrasena_editar_usuario.configure(show="●")

    def Ventana_editar_usuario(self):
        self.ventana_editar = tk.Toplevel(self)
        Configuracion_ventana(ventana=self.ventana_editar,ancho=600,alto=450,titulo="Editar usuario",no_modificar=True)
        sistema = platform.system()
        if sistema == "Windows":
            self.ventana_editar.iconbitmap(self.icono_app)

        elif sistema == 'Darwin':
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.ventana_editar.iconphoto(True, icon_photo)

        else:
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.ventana_editar.iconphoto(True, icon_photo)

        self.ventana_editar.transient(self)
        self.ventana_editar.grab_set()
        self.ventana_editar.focus_force()
        frame_principal = ttk.Frame(self.ventana_editar, padding=25)
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.pack(fill="both", expand=True)
        ttk.Label(frame_principal,text="Editar usuario",font=(" ", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 25))
        ttk.Label(frame_principal, text="Correo:").grid(row=1, column=0, sticky=tk.E, pady=10)
        ttk.Label(frame_principal, text="Rol:").grid(row=2, column=0, sticky=tk.E, pady=10)
        ttk.Label(frame_principal, text="Estado:").grid(row=3, column=0, sticky=tk.E, pady=10)
        self.correo_editar_usuario = ttk.Entry(frame_principal, width=35)
        self.correo_editar_usuario.insert(0,string=self.usuario_editar.username)
        self.Rol_editar_usuario = ttk.Combobox(frame_principal,values=Usuario.Rol,width=32,state="readonly")
        self.Estado_editar_usuario = ttk.Combobox(frame_principal,values=Usuario.Estado,width=32,state="readonly")
        if len(self.tabla_usuarios.get_children())==1 and self.tabla_usuarios.item(self.tabla_usuarios.selection()[0])['values'][2] == "Administrador":
            self.Rol_editar_usuario.set(value=self.usuario_editar.rol)
            self.Rol_editar_usuario.configure(state=tk.DISABLED)
        else:
            self.Rol_editar_usuario.set(value=self.usuario_editar.rol)
        self.Estado_editar_usuario.set(value=self.usuario_editar.bloqueado)
        self.correo_editar_usuario.grid(row=1, column=1, sticky=tk.W, pady=10)
        self.Rol_editar_usuario.grid(row=2, column=1, sticky=tk.W, pady=10)
        self.Estado_editar_usuario.grid(row=3, column=1, sticky=tk.W, pady=10)
        check_password = ttk.Checkbutton(frame_principal, text="Cambiar contraseña", variable=self.cambiar_password,command=self.habilitar_password)
        check_password.grid(row=4, column=1, sticky=tk.W)
        ttk.Label(frame_principal, text="Contraseña:").grid(row=5, column=0, sticky=tk.E, pady=10)
        frame_principal_2 = ttk.Frame(frame_principal)
        frame_principal_2.grid(row=5, column=1, sticky=tk.W, pady=10)
        self.contrasena_editar_usuario = ttk.Entry(frame_principal_2, width=31, show="●", state=tk.DISABLED)
        self.contrasena_editar_usuario_mostar = ttk.Button(frame_principal_2, image=self.imagen_icono_monstrar, width=2,command=lambda: self.Mostrar_ocultar_password_editar(event=None))
        self.contrasena_editar_usuario_mostar.bind("<Return>",self.Mostrar_ocultar_password_editar)
        self.contrasena_editar_usuario.grid(row=1, column=0, sticky=tk.E)
        self.contrasena_editar_usuario_mostar.grid(row=1, column=1, sticky=tk.E)
        ttk.Separator(frame_principal,orient="horizontal").grid(row=6,column=0,columnspan=2,sticky=tk.EW,pady=25)
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.grid(row=7,column=0,columnspan=2,pady=10)
        boton_guardar_editar_usuario=ttk.Button(frame_botones,text="Guardar",width=15,command=lambda :self.Guardar_usuario_editado(event=None))
        boton_guardar_editar_usuario.grid(row=0, column=0, padx=10)
        boton_cancelar_editar_usuario=ttk.Button(frame_botones,text="Cancelar",width=15,command=self.ventana_editar.destroy)
        boton_cancelar_editar_usuario.grid(row=0, column=1, padx=10)
        boton_guardar_editar_usuario.bind("<Return>",self.Guardar_usuario_editado)
        boton_cancelar_editar_usuario.bind("<Return>",lambda event: self.ventana_editar.destroy())

    def Ventana_creacion_usuario(self,event):
        self.ventana = tk.Toplevel(self)
        Configuracion_ventana(ventana=self.ventana,ancho=600,alto=450,titulo="Nuevo usuario",no_modificar=True)
        sistema = platform.system()
        if sistema == "Windows":
            self.ventana.iconbitmap(self.icono_app)

        elif sistema == 'Darwin':
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.ventana.iconphoto(True, icon_photo)
        else:
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.ventana.iconphoto(True, icon_photo)
        self.ventana.transient(self)
        self.ventana.grab_set()
        self.ventana.focus_force()
        frame_principal = ttk.Frame(self.ventana, padding=25)
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.pack(fill="both", expand=True)
        ttk.Label(frame_principal,text="Crear nuevo usuario",font=(" ", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 25))
        ttk.Label(frame_principal, text="Correo:").grid(row=1, column=0, sticky=tk.E, pady=10)
        ttk.Label(frame_principal, text="Contraseña:").grid(row=2, column=0, sticky=tk.E, pady=10)
        ttk.Label(frame_principal, text="Rol:").grid(row=3, column=0, sticky=tk.E, pady=10)
        ttk.Label(frame_principal, text="Estado:").grid(row=4, column=0, sticky=tk.E, pady=10)
        self.correo_nuevo_usuario = ttk.Entry(frame_principal, width=35)
        frame_principal_2 = ttk.Frame(frame_principal)
        self.Rol_nuevo_usuario = ttk.Combobox(frame_principal,values=Usuario.Rol,width=32,state="readonly")
        self.Estado_nuevo_usuario = ttk.Combobox(frame_principal,values=Usuario.Estado,width=32,state="readonly")
        self.Rol_nuevo_usuario.current(0)
        self.Estado_nuevo_usuario.current(1)
        self.correo_nuevo_usuario.grid(row=1, column=1, sticky=tk.W, pady=10)
        self.contrasena_nuevo_usuario = ttk.Entry(frame_principal_2, width=31, show="●")
        self.contrasena_nuevo_usuario_mostar = ttk.Button(frame_principal_2, image=self.imagen_icono_monstrar, width=2,command=lambda: self.Mostrar_ocultar_password(event=None),style="Inicio_sesion.TButton")
        self.contrasena_nuevo_usuario_mostar.bind("<Return>",self.Mostrar_ocultar_password)
        frame_principal_2.grid(row=2, column=1, sticky=tk.W, pady=10)
        self.contrasena_nuevo_usuario.grid(row=0,column=0,sticky=tk.E)
        self.contrasena_nuevo_usuario_mostar.grid(row=0,column=1,sticky=tk.E)
        self.Rol_nuevo_usuario.grid(row=3, column=1, sticky=tk.W, pady=10)
        self.Estado_nuevo_usuario.grid(row=4, column=1, sticky=tk.W, pady=10)
        ttk.Separator(frame_principal,orient="horizontal").grid(row=5,column=0,columnspan=2,sticky=tk.EW,pady=25)
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.grid(row=6,column=0,columnspan=2,pady=10)
        boton_guardar_nuevo_usuario=ttk.Button(frame_botones,text="Guardar",width=15,command=lambda :self.Guardar_usuario(event=None))
        boton_guardar_nuevo_usuario.grid(row=0, column=0, padx=10)
        boton_guardar_nuevo_usuario.bind("<Return>",self.Guardar_usuario)
        boton_cancelar_nuevo_usuario=ttk.Button(frame_botones,text="Cancelar",width=15,command=self.ventana.destroy)
        boton_cancelar_nuevo_usuario.grid(row=0, column=1, padx=10)
        boton_cancelar_nuevo_usuario.bind("<Return>",lambda event: self.ventana.destroy())

    def frame_tabla_registros(self):
        self.frame_tabla_logs = ttk.Frame(self.frame_gestion_logs, style="Banner.TFrame")
        self.frame_tabla_logs.columnconfigure(0, weight=10)
        self.frame_tabla_logs.columnconfigure(1,weight=0)
        self.frame_tabla_logs.rowconfigure(0, weight=10)
        self.frame_tabla_logs.rowconfigure(1, weight=0)
        self.tabla_logs = ttk.Treeview(self.frame_tabla_logs, columns=self.columna_tabla_logs,show="headings", cursor="hand2")
        self.tabla_logs.heading(column=0, text=self.columna_tabla_logs[0], anchor=tk.CENTER)
        self.tabla_logs.heading(column=1, text=self.columna_tabla_logs[1], anchor=tk.W)
        self.tabla_logs.heading(column=2, text=self.columna_tabla_logs[2], anchor=tk.W)
        self.tabla_logs.column(column=0, width=300, anchor=tk.CENTER,stretch=False)
        self.tabla_logs.column(column=1, width=300, anchor=tk.W,stretch=False)
        self.tabla_logs.column(column=2, width=550, anchor=tk.W,stretch=False)
        scroll_v = ttk.Scrollbar(self.frame_tabla_logs, orient=tk.VERTICAL, command=self.tabla_logs.yview,cursor="arrow")
        scroll_h = ttk.Scrollbar(self.frame_tabla_logs, orient=tk.HORIZONTAL, command=self.tabla_logs.xview,cursor="arrow")
        self.tabla_logs.configure(xscrollcommand=scroll_h.set)
        self.tabla_logs.configure(yscrollcommand=scroll_v.set)
        scroll_v.grid(row=0, column=1, sticky=tk.NS)
        scroll_h.grid(row=1, column=0,columnspan=2, sticky=tk.EW)
        self.tabla_logs.grid(row=0, column=0, sticky=tk.NSEW)
        self.frame_tabla_logs.grid(row=1,column=0,rowspan=6,sticky=tk.NSEW,padx=200,pady=20)

    def Cargar_datos_logs(self,usuario:str=None,accion:str=None):
        if self.lista_logs is None:
            self.lista_logs=DAOMedicalOmni3D.Seleccion_historial_acceso(usuario=usuario,accion=accion)
            for registro in self.lista_logs:
                self.tabla_logs.insert(parent="", index=tk.END, values=(registro.fecha,registro.username,registro.accion))

    def Cargar_lista_usuarios_logs(self):
        self.list_logs_usuarios = []
        self.lista_usuarios = DAOMedicalOmni3D.Seleccion_usuarios()
        if self.lista_usuarios:
            for usuario in self.lista_usuarios:
                self.list_logs_usuarios.append(usuario.username)
        self.list_logs_usuarios.insert(0, "Todos")

        if hasattr(self, "combox_usuarios"):
            self.combox_usuarios.configure(values=self.list_logs_usuarios)
            self.Eliminar_toda_tabla_logs()
            self.combox_usuarios.set("Todos")
            self.combox_acciones.set("Todos")
            self.Cargar_datos_logs(usuario=self.combox_usuarios.get(), accion=self.combox_acciones.get())



    def Filtrar_logs(self,event):
        self.Eliminar_toda_tabla_logs()
        self.Cargar_datos_logs(usuario=self.combox_usuarios.get(),accion=self.combox_acciones.get())

    def cambio_pestana(self, event):
        pestana_actual = self.notebook_admin.select()
        texto = self.notebook_admin.tab(pestana_actual, "text")
        if texto == "Registros":
            self.Cargar_lista_usuarios_logs()
    def limpiar_tabla_registro(self,event):
        self.combox_usuarios.set("Todos")
        self.combox_acciones.set("Todos")
        self.Eliminar_toda_tabla_logs()
        self.Cargar_datos_logs(usuario=self.combox_usuarios.get(), accion=self.combox_acciones.get())
    def gestion_log(self):
        self.tab_logs = ttk.Frame(self.notebook_admin,style="Menu_deslizable.TFrame")
        self.tab_logs.columnconfigure(0, weight=1)
        self.tab_logs.rowconfigure(0, weight=1)
        self.tab_logs.rowconfigure(1, weight=100)
        self.notebook_admin.add(self.tab_logs, text="Registros")
        ttk.Label(self.tab_logs, style="Menu_deslizable.TLabel", text="Gestión de Registros",font=(" ", 20, "bold")).grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        self.frame_gestion_logs = ttk.Frame(self.tab_logs, style="Admin.TFrame")
        self.frame_gestion_logs.columnconfigure(0, weight=1)
        self.frame_gestion_logs.rowconfigure(1, weight=5)
        self.frame_gestion_logs.rowconfigure(0, weight=1)
        self.frame_filtro_logs=ttk.Frame(self.frame_gestion_logs,style="Admin.TFrame")
        tk.Label( self.frame_filtro_logs,bg="#071640",foreground="white" ,text="Usuarios:").grid(row=0, column=0, padx=10, pady=20)
        self.combox_usuarios = ttk.Combobox( self.frame_filtro_logs,values=self.list_logs_usuarios,width=25,height=3,state="readonly",cursor="hand2")
        tk.Label(self.frame_filtro_logs,bg="#071640",foreground="white",text="Acciones:").grid(row=0, column=2, padx=5, pady=20)
        self.combox_acciones = ttk.Combobox(self.frame_filtro_logs, values= self.logs_accion,height=3,state="readonly",cursor="hand2")
        self.combox_acciones.current(0)
        self.boton_filtro = ttk.Button(self.frame_filtro_logs, text="Filtrar", cursor="hand2",command=lambda :self.Filtrar_logs(event=None))
        self.boton_limpiar = ttk.Button(self.frame_filtro_logs, text="Limpiar", cursor="hand2",command=lambda :self.limpiar_tabla_registro(event=None))
        self.boton_filtro.bind("<Return>",self.Filtrar_logs)
        self.boton_limpiar.bind("<Return>", self.limpiar_tabla_registro)
        self.combox_usuarios.grid(row=0, column=1, padx=5, pady=20)
        self.combox_acciones.grid(row=0, column=3, padx=5, pady=20)
        self.boton_filtro.grid(row=0, column=4, sticky=tk.W, padx=5, pady=20)
        self.boton_limpiar.grid(row=0,column=5,sticky=tk.W,padx=10,pady=20)
        self.frame_filtro_logs.grid(row=0,column=0)
        self.frame_gestion_logs.grid(row=1, column=0, sticky=tk.NSEW, padx=100, pady=20)
        self.frame_tabla_registros()
        self.combox_usuarios.set("Todos")
        self.Cargar_datos_logs(usuario=self.combox_usuarios.get(),accion=self.combox_acciones.get())

        #self.frame_botones_usuarios_gestion()
    def gestion_log_2(self):
        self.tab_logs = ttk.Frame(self.notebook_admin)
        self.notebook_admin.add(self.tab_logs, text="Registros")
        ttk.Label(self.tab_logs, text="Registros del sistema").pack(pady=20)
    def Logo_banner(self):
        self.label_logo=ttk.Label(self.frame_banner,style="Banner.TLabel",image=self.imagen_principal)
        self.label_logo.pack(side=tk.LEFT,padx=10)
        self.label_username = ttk.Label(self.frame_banner, style="Banner.TLabel",image=self.imagen_user,text=self.usuario.username, compound=tk.LEFT)
        self.label_username.pack(side=tk.RIGHT, padx=20)

    def Mostrar_ocultar_indicador(self, indicador_2, page, animar=True):
        for boton in self.botones_menu:
            if isinstance(boton["widget"], list):
                boton["widget"][1].configure(style="Indicador_menu_deslizable_off.TLabel")
        indicador_2.configure(style="Indicador_menu_deslizable_onn.TLabel")

        if page != self.Confirmar_salida:
            if animar:
                self._transicion_pagina(page)
            else:
                for frame in [f for f in self.frame_page.winfo_children()]:
                    frame.destroy()
                if callable(page):
                    page()
        elif callable(page):
            page()

    def _transicion_pagina(self, page):
        if not hasattr(self, "_overlay") or not self._overlay.winfo_exists():
            self._overlay = tk.Frame(self.frame_page, bg="#C7C7C7")
        self._overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self._overlay.lift()
        self.update_idletasks()
        self.Ocultar_paginas()
        if callable(page):
            page()
        self._overlay.lift()
        self.update_idletasks()
        self._overlay.place_forget()

    def Creacion_menu_deslizable(self):
        if self.usuario.rol == Usuario.Rol[1]:
            self.botones_menu.append(
                {"nombre": "Administrar cuenta", "imagen": self.imagen_admin, "y": 300, "comand": self.Pagina_admin})

        for boton_info in self.botones_menu:
            boton = ttk.Button(self.frame_menu, image=boton_info["imagen"], style="Menu_deslizable.TButton",cursor="hand2")
            boton.place(x=10, y=boton_info["y"], width=60, height=40)
            indicador = ttk.Label(self.frame_menu, style="Indicador_menu_deslizable_off.TLabel")
            indicador.place(x=8, y=boton_info["y"], height=40)
            label = ttk.Label(self.frame_menu, text=boton_info["nombre"], style="Menu_deslizable.TLabel",cursor="hand2")
            label.place(x=80, y=boton_info["y"] + 10, width=160)
            boton_info["widget"] = [boton, indicador, label]
            label.bind("<Button-1>",lambda event, ind=indicador, funcion=boton_info["comand"]:self.Mostrar_ocultar_indicador(indicador_2=ind, page=funcion, animar=True))
            boton.configure(command=lambda ind=indicador, funcion=boton_info["comand"]: self.Mostrar_ocultar_indicador(indicador_2=ind, page=funcion, animar=True))
        for boton_info in self.botones_menu:
            if boton_info["nombre"] == "Banco de imágenes":
                ind = boton_info["widget"][1]
                funcion = boton_info["comand"]
                self.Mostrar_ocultar_indicador(indicador_2=ind, page=funcion, animar=False)



    def Confirmar_salida(self):
        ventana = tk.Toplevel(self)
        Configuracion_ventana(ventana=ventana,ancho=300,alto=120,titulo="Confirmar salida",no_modificar=True)
        sistema = platform.system()
        if sistema == "Windows":
            ventana.iconbitmap(self.icono_app)

        elif sistema == 'Darwin':
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            ventana.iconphoto(True, icon_photo)

        else:
            icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
            icon_photo = ImageTk.PhotoImage(icon_img)
            ventana.iconphoto(True, icon_photo)

        ventana.transient(self)
        ventana.focus_force()
        ventana.grab_set()
        ventana.protocol("WM_DELETE_WINDOW", lambda: None)


        def Evitar_minimizar(event):
            self.deiconify()
            ventana.lift()
            ventana.focus_force()
        self.bind("<Unmap>", Evitar_minimizar)
        label = tk.Label(ventana,background="#082B78",foreground="white",text="¿Desea cerrar sesion?")
        label.pack(pady=20)
        frame_botones = tk.Frame(ventana,background="#082B78")
        frame_botones.pack()
        def cancelar(event):
            self.unbind("<Unmap>")
            ventana.destroy()
        boton_si = ttk.Button(frame_botones,text="Salir",command=lambda :self.cerrar_sesion(event=None))
        boton_si.bind("<Return>",self.cerrar_sesion)
        boton_no = ttk.Button(frame_botones,text="Cancelar",command=lambda :cancelar(event=None))
        boton_no.bind("<Return>",cancelar)
        boton_si.pack(side="left", padx=10)
        boton_no.pack(side="right", padx=10)
        self.wait_window(ventana)

    def Almacenamiento_imagenes(self, evento):
        try:
            # ✅ Siempre recargar desde disco al inicio para garantizar estado fresco
            with open(self.archivojson, "r") as f:
                self.configuracion_sistema = json.load(f)

            sistema = platform.system()
            initialdir = (
                    self.configuracion_sistema.get("path_import_imagen") or os.path.expanduser("~")
            )

            if sistema == 'Darwin':
                rutas_raw = filedialog.askopenfiles(
                    title="Seleccione las imágenes para importar (.nii.gz)",
                    initialdir=initialdir
                )
                rutas = [r for r in rutas_raw if r.name.endswith('.nii.gz')] if rutas_raw else []
                if rutas_raw and not rutas:
                    messagebox.showwarning(
                        title="Advertencia",
                        message="Ningún archivo seleccionado tiene extensión .nii.gz válida."
                    )
                    self.frame_botones.focus()
                    return
            else:
                tipos = [("Imágenes Médicas (NIfTI / Standard)", (".nii.gz",))]
                rutas = filedialog.askopenfiles(
                    title="Seleccione las imágenes para importar",
                    initialdir=initialdir,
                    filetypes=tipos
                )

            if rutas:
                self.configuracion_sistema["path_import_imagen"] = os.path.dirname(rutas[0].name)
                with open(self.archivojson, "w") as f:
                    json.dump(self.configuracion_sistema, f, indent=4)

                listado_imagnes_importadas = []
                for ruta_imagen in rutas:
                    shutil.copy(ruta_imagen.name, Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"])
                    nombre_imagen = os.path.basename(ruta_imagen.name).split(".")[0]
                    texto = f"{self.usuario.ACCIONES[3]}: {nombre_imagen}"
                    DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
                    Configuracionnnunetv2.Cifrar_imagenes(path_imagen=ruta_imagen.name)
                    listado_imagnes_importadas.append(nombre_imagen)

                nombres_imagenes = ",".join(listado_imagnes_importadas)
                self.Cargar_imagenes()
                messagebox.showinfo(
                    title="Importación imagenes",
                    message=f"Se importaron correctamente las siguientes imágenes: {nombres_imagenes}"
                )

            self.frame_botones.focus()

        except Exception as e:
            log.error(f"Error al importar las imagenes:\n{e}")
if __name__=="__main__":
    usuario=Usuario(id_usuario=4,username="andresf@gmial.com",password="12345",rol="admin",intentos_fallidos=0,bloqueado=0)
    user=Usuario(id_usuario=1, username="felipe14@gmail.com", password="12345", rol="Administrador", intentos_fallidos=0, bloqueado=0)
    Ventana_Principal_MedicalOmni3D(usuario=user).mainloop()