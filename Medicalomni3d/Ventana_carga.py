import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import multiprocessing
import sys,os,platform
from Medicalomni3d.Configuracion_medicalomni3d import Configuracion_ventana, Estilos, resource_path
from Medicalomni3d.Configuracion_Apcivmapcas import Configuracionnnunetv2
from Medicalomni3d.Dao_medicalomni3d import DAOMedicalOmni3D

class VentanaCargaSubproceso(tk.Toplevel):
    def __init__(self, master, usuario,lista_imagenes_tabla,imagenes_codificadas,espaciado_orig,congiguracion,callback=None):
        super().__init__(master)
        self.usuario=usuario
        self.callback=callback
        self.master=master
        self.proceso_procesamiento = None
        self.subproceso_gpu = None
        self.cancelado = False
        Estilos()
        self.lista_imagenes_tabla=lista_imagenes_tabla
        self.imagenes_codificadas = imagenes_codificadas
        self.modelo_seleccionado = congiguracion["modelo_seleccionado"]
        self.dispositivo = congiguracion['modelos'][self.modelo_seleccionado]["device"]
        self.nuevo_espaciado=congiguracion['modelos'][self.modelo_seleccionado]["nuevo_espaciado"]
        self.normalizacion=congiguracion['modelos'][self.modelo_seleccionado]["Normalizacion"]
        self.aplicar_espaciado = congiguracion['modelos'][self.modelo_seleccionado]["Espaciado"]
        self.espaciado_orig = espaciado_orig
        Configuracion_ventana(ventana=self,ancho=350,alto=130,titulo="Ejecutando Inferencia",no_modificar=True)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.lbl = tk.Label(self,text="Preparando entorno...", bg="#082B78",font=(" ", 10, "bold"),foreground="white")
        self.boton_cancelar=ttk.Button(self,text="Cancelar",command=self.Cancelar_ejecucion)
        self.progreso = ttk.Progressbar(self, mode="indeterminate", length=280)
        self.lbl.pack(pady=10)
        self.progreso.pack(pady=5)
        self.boton_cancelar.pack(anchor=tk.E,pady=10,padx=20)
        self.progreso.start(12)
        self.after(150, self.iniciar_fase_1_proceso)
        try:
            if platform.system() == "Windows":
                self.iconbitmap(resource_path("medicalomni3d.ico"))
            else:
                from PIL import Image, ImageTk
                icon_img = Image.open(resource_path("medicalomni3d.png"))
                icon_photo = ImageTk.PhotoImage(icon_img)
                self._icon_photo = icon_photo
                self.iconphoto(True, icon_photo)
        except Exception:
            pass

    def iniciar_fase_1_proceso(self):

        if self.cancelado:
            return
        self.lbl.config(text="Fase 1/3: Procesando imágenes en segundo plano..." )
        try:
            ctx = multiprocessing.get_context("spawn")

            self.proceso_procesamiento = ctx.Process(target=Configuracionnnunetv2.Procesamiento_completo,args=(self.imagenes_codificadas,self.normalizacion,self.aplicar_espaciado,self.nuevo_espaciado))

            self.proceso_procesamiento.start()

            self.after(100, self.monitorear_fase_1)

        except Exception as e:
            self.grab_release()
            self.destroy()

            messagebox.showerror(
                "Error Inferencia",
                f"No se pudo inicializar el entorno de multiproceso:\n{e}"
            )

    def monitorear_fase_1(self):

        if self.cancelado:
            return

        if self.proceso_procesamiento is None:
            return

        if self.proceso_procesamiento.is_alive():
            self.after(200, self.monitorear_fase_1)
        else:

            if self.cancelado:
                return

            if self.proceso_procesamiento.exitcode == 0:
                for imagen in self.lista_imagenes_tabla:
                    if imagen in os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"]):
                        os.remove(os.path.join(Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"],imagen))
                self.fase_2_inferencia()
            else:
                self.grab_release()
                self.destroy()

                messagebox.showerror("Error Inferencia","El procesamiento de imágenes falló.")

    def Cancelar_ejecucion(self):

        self.cancelado = True

        self.lbl.config(text="Cancelando proceso...")
        self.boton_cancelar.config(state="disabled")

        try:
            self.progreso.stop()
        except:
            pass
        try:
            if (self.proceso_procesamiento is not None and self.proceso_procesamiento.is_alive()):
                self.proceso_procesamiento.terminate()
                self.proceso_procesamiento.join(timeout=2)
                if os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                    Configuracionnnunetv2.Eliminacion_json_salida()
                    for imagen in os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                        os.remove(os.path.join(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"], imagen))
                for imagen in self.lista_imagenes_tabla:
                    if imagen in os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"]):
                        os.remove(os.path.join(Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"],imagen))

        except Exception:
            pass
        try:
            if (self.subproceso_gpu is not None and self.subproceso_gpu.is_alive()):
                self.subproceso_gpu.terminate()
                if os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                    Configuracionnnunetv2.Eliminacion_json_salida()
                    for imagen in os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                        os.remove(os.path.join(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"], imagen))
                self.subproceso_gpu.join(timeout=5)
                if self.subproceso_gpu.is_alive():
                    self.subproceso_gpu.kill()
                    self.subproceso_gpu.join()
        except Exception:
            pass

        try:
            self.grab_release()
        except:
            pass

        self.destroy()

    def fase_2_inferencia(self):
        self.lbl.config(text=f"Fase 2/3: Ejecutando inferencia...")
        self.update()

        self.subproceso_gpu = Configuracionnnunetv2.Inferencias_modelo_asincrona(modelo_selecionado=self.modelo_seleccionado,device=self.dispositivo)
        if self.subproceso_gpu:
            self.monitorear_subproceso()
        else:
            self.grab_release()
            self.destroy()
            if os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                Configuracionnnunetv2.Eliminacion_json_salida()
                for imagen in  os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                    os.remove(os.path.join(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"],imagen))
            messagebox.showerror("Error Inferencia", "No se pudo comunicar con el ejecutable del modelo.")

    def monitorear_subproceso(self):

        if self.cancelado:
            return

        if self.subproceso_gpu is None:
            return

        if self.subproceso_gpu.is_alive():
            self.after(500, self.monitorear_subproceso)
            return

        if self.cancelado:
            return

        if self.subproceso_gpu.exitcode == 0:
            self.fase_3_restauracion()
        else:
            self.grab_release()
            self.destroy()
            if os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                Configuracionnnunetv2.Eliminacion_json_salida()
                for imagen in  os.listdir(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]):
                    os.remove(os.path.join(Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"],imagen))
            messagebox.showerror("Error Inferencia","La inferencia terminó con errores.")
    def fase_3_restauracion(self):
        self.boton_cancelar.config(state=tk.DISABLED)
        self.lbl.config(text="Fase 3/3: Reestableciendo espaciados originales...")
        self.update()
        Configuracionnnunetv2.Restaurar_espaciado_original(diccionario_paths=self.imagenes_codificadas,diccionario_spacings=self.espaciado_orig,espaciado=True)
        self.grab_release()
        self.destroy()
        nombre_imagen = ",".join(self.lista_imagenes_tabla)
        texto = f"{self.usuario.ACCIONES[6]}: {nombre_imagen}"
        DAOMedicalOmni3D.Insertar_registro_intento(self.usuario, texto)
        messagebox.showinfo("Éxito", "¡Procesamiento completo e inferencia finalizados exitosamente!")

        if self.callback:
            self.callback()