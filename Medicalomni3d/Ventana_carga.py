import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import multiprocessing
import sys,os,platform
import subprocess
from Medicalomni3d.Control_procesos import crear_job, IS_WINDOWS
from Medicalomni3d.Configuracion_medicalomni3d import Configuracion_ventana, Estilos, resource_path
from Medicalomni3d.Configuracion_Apcivmapcas import Configuracionnnunetv2
from Medicalomni3d.Dao_medicalomni3d import DAOMedicalOmni3D
from Medicalomni3d.loggin_MedicalOmni3d import log

try:
    from ctypes import windll
    myappid = 'andresCA.MedicalOmni3D.subproduct.1.0.0.0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class VentanaCargaSubproceso(tk.Toplevel):
    def __init__(self, master, usuario,lista_imagenes_tabla,imagenes_codificadas,espaciado_orig,congiguracion,callback=None):
        super().__init__(master)
        self.usuario=usuario
        self.callback=callback
        self.master=master
        self.proceso_procesamiento = None
        self.subproceso_gpu = None
        self.cancelado = False
        self.ctx = multiprocessing.get_context("spawn")
        self.evento_listo_fase1 = None
        self.evento_cancelar_fase1 = None
        self.evento_listo_fase2 = None
        self.proceso_procesamiento = None
        self.subproceso_gpu = None
        self.job_fase1 = None
        self.job_fase2 = None
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
            ctx = self.ctx

            self.evento_listo_fase1 = ctx.Event()
            self.evento_cancelar_fase1 = ctx.Event()

            self.proceso_procesamiento = ctx.Process(
                target=Configuracionnnunetv2.Procesamiento_completo,
                args=(self.imagenes_codificadas, self.normalizacion, self.aplicar_espaciado, self.nuevo_espaciado),
                kwargs={
                    "evento_listo": self.evento_listo_fase1,
                    "evento_cancelar": self.evento_cancelar_fase1,
                }
            )

            self.proceso_procesamiento.start()
            self.job_fase1 = crear_job()
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

        if self._esta_vivo(self.proceso_procesamiento):
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

    def _esta_vivo(self, proceso):
        if proceso is None:
            return False
        try:
            return proceso.is_alive()
        except Exception:
            try:
                pid = proceso.pid
            except Exception:
                pid = None
            return self._pid_sigue_vivo(pid)

    @staticmethod
    def _pid_sigue_vivo(pid):
        if pid is None:
            return False
        if platform.system() != "Windows":
            try:
                os.kill(pid, 0)
                return True
            except ProcessLookupError:
                return False
            except PermissionError:
                return True
            except Exception:
                return True
        try:
            resultado = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True
            )
            return str(pid) in resultado.stdout
        except Exception:
            return True

    def _matar_proceso_seguro(self, proceso, job=None, timeout=3):
        if job is not None:
            try:
                job.terminar()
                if not IS_WINDOWS:
                    try:
                        if proceso is not None:
                            proceso.join(timeout=1)
                    except Exception:
                        pass
                    job.matar_fuerte()
            except Exception as e:
                log.error(f"Error terminando job object: {e}")

        if proceso is None:
            if job is not None:
                try:
                    job.cerrar()
                except Exception:
                    pass
            return

        try:
            pid = proceso.pid
        except Exception:
            pid = None

        if pid is None:
            if job is not None:
                try:
                    job.cerrar()
                except Exception:
                    pass
            return

        try:
            proceso.terminate()
        except Exception:
            pass
        try:
            proceso.join(timeout=timeout)
        except Exception:
            pass
        try:
            proceso.kill()
        except Exception:
            pass
        try:
            proceso.join(timeout=timeout)
        except Exception:
            pass

        if self._pid_sigue_vivo(pid):
            try:
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/F", "/PID", str(pid), "/T"], capture_output=True)
                else:
                    import signal
                    os.kill(pid, signal.SIGKILL)
            except Exception:
                pass

        if self._pid_sigue_vivo(pid):
            try:
                log.critical(
                    f"No se pudo terminar el proceso huérfano con PID {pid} tras agotar terminate()/kill()/taskkill.")
            except Exception:
                pass

        if job is not None:
            try:
                job.cerrar()
            except Exception:
                pass

    def _limpiar_carpeta_procesamiento(self):
        try:
            carpeta = Configuracionnnunetv2.PATH_DICT["nnUNet_Procesamiento_imagenes"]
            if os.listdir(carpeta):
                Configuracionnnunetv2.Eliminacion_json_salida()
                for imagen in os.listdir(carpeta):
                    try:
                        os.remove(os.path.join(carpeta, imagen))
                    except Exception:
                        pass
        except Exception:
            pass

    def _limpiar_carpeta_almacenamiento(self):
        try:
            carpeta = Configuracionnnunetv2.PATH_DICT["nnUNet_Almacenamiento_imagenes"]
            existentes = os.listdir(carpeta)
            for imagen in self.lista_imagenes_tabla:
                if imagen in existentes:
                    try:
                        os.remove(os.path.join(carpeta, imagen))
                    except Exception:
                        pass
        except Exception:
            pass

    def Cancelar_ejecucion(self):

        self.cancelado = True

        self.lbl.config(text="Cancelando proceso...")
        self.boton_cancelar.config(state="disabled")

        try:
            self.progreso.stop()
        except:
            pass

        try:
            if self.evento_cancelar_fase1 is not None:
                self.evento_cancelar_fase1.set()
        except Exception:
            pass

        self._cancelar_fase1_seguro()

    def _cancelar_fase1_seguro(self, intentos=0):

        proceso = self.proceso_procesamiento
        try:
            sigue_vivo = proceso is not None and proceso.is_alive()
        except Exception:
            sigue_vivo = proceso is not None

        if sigue_vivo:
            listo = self.evento_listo_fase1 is not None and self.evento_listo_fase1.is_set()
            if not listo and intentos < 30:
                self.after(100, lambda: self._cancelar_fase1_seguro(intentos + 1))
                return
            if listo and self.job_fase1 is not None and proceso is not None:
                try:
                    self.job_fase1.asignar_pid(proceso.pid)
                except Exception:
                    pass

        self._matar_proceso_seguro(proceso,job=self.job_fase1, timeout=2)
        self._limpiar_carpeta_procesamiento()
        self._limpiar_carpeta_almacenamiento()
        self._cancelar_fase2_seguro()

    def _cancelar_fase2_seguro(self, intentos=0):
        proceso = self.subproceso_gpu
        try:
            sigue_vivo = proceso is not None and proceso.is_alive()
        except Exception:
            sigue_vivo = proceso is not None

        if sigue_vivo:
            listo = self.evento_listo_fase2 is not None and self.evento_listo_fase2.is_set()
            if not listo and intentos < 80:
                self.after(100, lambda: self._cancelar_fase2_seguro(intentos + 1))
                return
            if platform.system()!="Windows":
                if listo and self.job_fase2 is not None and proceso is not None:
                    try:
                        self.job_fase2.asignar_pid(proceso.pid)
                    except Exception:
                        pass

        self._matar_proceso_seguro(proceso,job=self.job_fase2, timeout=5)
        self._limpiar_carpeta_procesamiento()
        try:
            Configuracionnnunetv2.Matar_procesos_huerfanos()
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
        self.evento_listo_fase2 = multiprocessing.Event()
        self.subproceso_gpu = Configuracionnnunetv2.Inferencias_modelo_asincrona(modelo_selecionado=self.modelo_seleccionado,device=self.dispositivo,evento_listo=self.evento_listo_fase2)
        self.job_fase2 = crear_job()
        if self.subproceso_gpu:
            self.monitorear_subproceso()
            if platform.system()=="Windows":
                self.job_fase2.asignar_pid(self.subproceso_gpu.pid)
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

        if self._esta_vivo(self.subproceso_gpu):
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