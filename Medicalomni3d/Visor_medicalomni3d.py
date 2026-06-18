import SimpleITK as sitk
import vtk
from vtk.util import numpy_support
import numpy as np
import colorsys
import platform
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from Medicalomni3d.loggin_MedicalOmni3d import log
from Medicalomni3d.Configuracion_medicalomni3d import Estilos

class Visor_MedicalOmni3D:
    def __init__(self, frame_visualizador,imagen:str=None):
        self.interactor = None
        self.render_window = None
        self.renderer = None
        Estilos()
        self.imagen=imagen
        self.mascara=None
        self.img_tk_sagital = None
        self.img_tk_coronal = None
        self.img_tk_axial = None
        self.canvas_coronal = None
        self.frame_3d = None
        self.frame_coronal = None
        self.frame_sagital = None
        self.frame_axial = None
        self.start_x = None
        self.zoom_axial=1.0
        self.zoom_coronal = 1.0
        self.zoom_sagital = 1.0
        self.start_y = None
        self.canvas_axial = None
        self.canvas_sagital = None
        self.canvas_3d = None
        self.maximo_sagital = 100
        self.maximo_coronal = 100
        self.maximo_axial = 100
        self.slider_sagital = None
        self.slider_coronal = None
        self.slider_axial = None
        self.frame_visualizador=frame_visualizador
        self.array_imagen = None
        self.slice_axial = 0
        self.slice_coronal = 0
        self.slice_sagital = 0
        self.offset_axial_x = 0
        self.offset_axial_y = 0
        self.offset_coronal_x = 0
        self.offset_coronal_y = 0
        self.offset_sagital_x = 0
        self.offset_sagital_y = 0

        # --- Soporte 4D (3D + tiempo) ---
        self.es_4d = False
        self.slice_tiempo = 0

        # --- Espaciado de voxel (para corregir proporciones en cortes anisotrópicos) ---
        self.spacing_x = 1.0
        self.spacing_y = 1.0
        self.spacing_z = 1.0

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.0, 0.0, 0.0)
        if self.imagen:
            self.Obtencion_imagen()
        self.Frame_visor()
        self.Canvas_visor()
        self.slider_visor()
        self.inicializar_vtk_seguro(mascara=self.mascara)




    def Obtencion_imagen(self):
        try:
            if self.imagen:
                imagen = sitk.ReadImage(self.imagen)
                dimension = imagen.GetDimension()

                if dimension == 3:
                    imagen = sitk.DICOMOrient(imagen, "LPS")
                    self.es_4d = False
                elif dimension == 4:
                    # DICOMOrient no soporta imágenes 4D, se omite
                    self.es_4d = True
                else:
                    self.es_4d = False

                self.array_imagen = sitk.GetArrayFromImage(imagen)
                espaciado = imagen.GetSpacing()
                self.spacing_x = espaciado[0] if len(espaciado) > 0 else 1.0
                self.spacing_y = espaciado[1] if len(espaciado) > 1 else 1.0
                self.spacing_z = espaciado[2] if len(espaciado) > 2 else 1.0

                if self.es_4d:
                    self.slice_tiempo = 0
                    volumen = self.array_imagen[self.slice_tiempo]
                else:
                    self.slice_tiempo = 0
                    volumen = self.array_imagen

                self.slice_axial = volumen.shape[0] // 2
                self.slice_coronal = volumen.shape[1] // 2
                self.slice_sagital = volumen.shape[2] // 2
                self.maximo_axial = volumen.shape[0] - 1
                self.maximo_coronal = volumen.shape[1] - 1
                self.maximo_sagital = volumen.shape[2] - 1

        except Exception as e:
            log.error(f"Error en la visualizacion de la imagen:\n{e}")

    def Frame_visor(self):
        self.frame_visualizador.rowconfigure(0, weight=1)
        self.frame_visualizador.rowconfigure(1, weight=1)
        self.frame_visualizador.columnconfigure(0, weight=1)
        self.frame_visualizador.columnconfigure(1, weight=1)
        self.frame_axial=ttk.Frame(self.frame_visualizador,style="Page_configuracion_banco.TFrame")
        self.frame_coronal = ttk.Frame(self.frame_visualizador,style="Page_configuracion_banco.TFrame")
        self.frame_sagital=ttk.Frame(self.frame_visualizador,style="Page_configuracion_banco.TFrame")
        self.frame_3d =ttk.Frame(self.frame_visualizador,style="Page_configuracion_banco.TFrame")
        self.frame_axial.grid(row=0,column=0,sticky=tk.NSEW)
        self.frame_3d.grid(row=0,column=1,sticky=tk.NSEW)
        self.frame_coronal.grid(row=1,column=0,sticky=tk.NSEW)
        self.frame_sagital.grid(row=1,column=1,sticky=tk.NSEW)

    def Limpiar_3d(self):
        if self.renderer:
            self.renderer.RemoveAllViewProps()
            self.renderer.ResetCamera()

        if self.render_window:
            self.render_window.Render()

    def Cargar_3d(self, renderer=None, mascara=None):
        renderer = renderer if renderer is not None else self.renderer
        mascara = mascara if mascara is not None else self.mascara

        if not mascara:
            return

        renderer.RemoveAllViewProps()
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(mascara)
        reader.Update()
        image = reader.GetOutput()
        vtk_array = image.GetPointData().GetScalars()
        numpy_data = np.unique(numpy_support.vtk_to_numpy(vtk_array))[1:]
        colores = {seg: colorsys.hsv_to_rgb(i / len(numpy_data), 1.0, 1.0) for i, seg in enumerate(numpy_data)}

        for clase, color_rgb in colores.items():
            marching = vtk.vtkDiscreteMarchingCubes()
            marching.SetInputConnection(reader.GetOutputPort())
            marching.GenerateValues(1, clase, clase)
            smooth = vtk.vtkSmoothPolyDataFilter()
            smooth.SetInputConnection(marching.GetOutputPort())
            smooth.SetNumberOfIterations(15)
            smooth.SetRelaxationFactor(0.2)
            smooth.FeatureEdgeSmoothingOff()
            smooth.BoundarySmoothingOn()
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputConnection(smooth.GetOutputPort())
            normals.SetFeatureAngle(60.0)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(normals.GetOutputPort())
            mapper.ScalarVisibilityOff()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(color_rgb)
            actor.GetProperty().SetOpacity(1.0)
            actor.GetProperty().SetInterpolationToPhong()
            renderer.AddActor(actor)

    def inicializar_vtk_seguro(self, mascara: str = None):
        sistema = platform.system()
        if sistema == "Darwin":
            self.mascara = mascara if mascara else None
            lbl_mac = tk.Label(
                self.frame_3d,
                text="Visualizador Médico 3D (macOS)\n\nEl motor gráfico requiere una ejecución externa\npara evitar fallos de memoria en el sistema.",
                justify=tk.CENTER, bg="#1a1a1a", fg="white", font=("Arial", 12)
            )
            lbl_mac.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            btn_abrir_3d = ttk.Button(
                self.frame_3d,
                text="Abrir Renderizador Volumétrico",
                command=self.abrir_ventana_vtk_mac
            )
            btn_abrir_3d.place(relx=0.5, rely=0.65, anchor=tk.CENTER)
        else:
            window_id = self.frame_3d.winfo_id()
            try:
                self.render_window = vtk.vtkRenderWindow()
                self.interactor = vtk.vtkRenderWindowInteractor()
                self.interactor.SetRenderWindow(self.render_window)
                if sistema == "Windows":
                    import sys
                    puntero_void_str = f"_{window_id:016x}_p_void" if sys.maxsize > 2 ** 32 else f"_{window_id:08x}_p_void"
                    self.render_window.SetParentId(puntero_void_str)
                else:
                    self.render_window.SetWindowId(window_id)

                self.render_window.AddRenderer(self.renderer)
                if mascara:
                    self.mascara = mascara
                    self.Cargar_3d()
                else:
                    self.mascara = None
                    self.Limpiar_3d()
                ancho = self.frame_3d.winfo_width()
                alto = self.frame_3d.winfo_height()
                self.render_window.SetSize(ancho, alto)
                self.renderer.ResetCamera()
                self.render_window.Render()
                self.interactor.Initialize()
                self.frame_3d.bind("<Configure>", self.on_resize)
            except ImportError:
                pass
    def destruir_visor(self):
        try:
            if self.interactor:
                self.interactor.TerminateApp()
                self.interactor = None
            if self.render_window:
                self.render_window.Finalize()
                self.render_window = None
            if self.renderer:
                self.renderer.RemoveAllViewProps()
                self.renderer = None
        except Exception as e:
            log.error(f"Error al destruir el visor VTK: {e}")

    def on_resize(self, event):
        self.render_window.SetSize(event.width, event.height)
        self.render_window.Render()
    def abrir_ventana_vtk_mac(self):
        try:
            renderer = vtk.vtkRenderer()
            render_window = vtk.vtkRenderWindow()
            render_window.AddRenderer(renderer)
            interactor = vtk.vtkRenderWindowInteractor()
            interactor.SetRenderWindow(render_window)
            renderer.SetBackground(0.0, 0.0, 0.0)
            if self.mascara:
                self.Cargar_3d(renderer=renderer, mascara=self.mascara)
            else:
                messagebox.showinfo("Visor 3D","No hay una máscara cargada para visualizar en 3D.")
                return
            render_window.SetWindowName("MedicalOmni3D - Visor Independiente macOS")
            render_window.SetSize(800, 600)
            renderer.ResetCamera()
            render_window.Render()
            interactor.Initialize()
            interactor.Start()
        except ImportError:
            messagebox.showerror("Error de Dependencias", "La librería VTK no está instalada en este entorno Mac.")
        except Exception as e:
            messagebox.showerror("Error en visor 3D", f"No se pudo abrir el visor 3D:\n{e}")


    def zoom_mouse(self, event,vista):
      try:
          if vista:
              if vista == "axial":
                  if event.delta > 0:
                      self.zoom_axial *= 1.1
                  else:
                      self.zoom_axial /= 1.1
                  self.dibujar(vista="axial")
              elif vista == "coronal":
                  if event.delta > 0:
                      self.zoom_coronal *= 1.1
                  else:
                      self.zoom_coronal /= 1.1
                  self.dibujar(vista="coronal")
              else:
                  if event.delta > 0:
                      self.zoom_sagital *= 1.1
                  else:
                      self.zoom_sagital /= 1.1
                  self.dibujar(vista="sagital")

      except Exception as e:
          log.error(f"Error en la manupilacion del  zoom:\n{e} ")

    def iniciar_arrastre(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def arrastrar(self, event, vista):
        try:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            if vista == "axial":
                self.offset_axial_x += dx
                self.offset_axial_y += dy
            elif vista == "coronal":
                self.offset_coronal_x += dx
                self.offset_coronal_y += dy
            elif vista == "sagital":
                self.offset_sagital_x += dx
                self.offset_sagital_y += dy
            self.start_x = event.x
            self.start_y = event.y
            self.dibujar(vista)

        except Exception as e:
            log.error(f"Error en arrastrar la imagen:\n{e}")

    def Canvas_visor(self):
        self.canvas_axial = tk.Canvas(self.frame_axial, bg="black")
        self.canvas_coronal = tk.Canvas(self.frame_coronal, bg="black")
        self.canvas_sagital = tk.Canvas(self.frame_sagital, bg="black")
        self.canvas_axial.pack(side=tk.BOTTOM, fill=tk.BOTH,expand=True)
        self.canvas_coronal.pack(side=tk.BOTTOM, fill=tk.BOTH,expand=True)
        self.canvas_sagital.pack(side=tk.BOTTOM, fill=tk.BOTH,expand=True)
        self.canvas_axial.bind("<MouseWheel>",lambda e: self.zoom_mouse(e, "axial"))
        self.canvas_coronal.bind("<MouseWheel>",lambda e: self.zoom_mouse(e, "coronal"))
        self.canvas_sagital.bind("<MouseWheel>",lambda e: self.zoom_mouse(e, "sagital"))
        self.canvas_axial.bind("<Button-1>",self.iniciar_arrastre)
        self.canvas_axial.bind("<B1-Motion>",lambda e: self.arrastrar(e, "axial"))
        self.canvas_coronal.bind("<Button-1>",self.iniciar_arrastre)
        self.canvas_coronal.bind("<B1-Motion>",lambda e: self.arrastrar(e, "coronal"))
        self.canvas_sagital.bind("<Button-1>",self.iniciar_arrastre)
        self.canvas_sagital.bind("<B1-Motion>",lambda e: self.arrastrar(e, "sagital"))

    def dibujar(self,vista:str=None):
        if vista:
            img = self.Get_imagen_actual(vista)
            if img is None:
                return
            w, h = img.size

            # Espaciado mínimo como referencia para que las vistas isotrópicas
            # se comporten igual que antes (factor = 1)
            min_spacing = min(self.spacing_x, self.spacing_y, self.spacing_z)
            if min_spacing <= 0:
                min_spacing = 1.0

            if vista=="axial":
                factor_w = self.spacing_x / min_spacing
                factor_h = self.spacing_y / min_spacing
                nuevo_w = max(1, int(w * self.zoom_axial * factor_w))
                nuevo_h = max(1, int(h * self.zoom_axial * factor_h))
                img = img.resize((nuevo_w, nuevo_h))
                self.img_tk_axial = ImageTk.PhotoImage(img)
                self.canvas_axial.delete(tk.ALL)
                self.canvas_axial.create_image(self.offset_axial_x,self.offset_axial_y,anchor=tk.NW,image=self.img_tk_axial)
            elif vista=="coronal":
                factor_w = self.spacing_x / min_spacing
                factor_h = self.spacing_z / min_spacing
                nuevo_w = max(1, int(w * self.zoom_coronal * factor_w))
                nuevo_h = max(1, int(h * self.zoom_coronal * factor_h))
                img = img.resize((nuevo_w, nuevo_h))
                self.img_tk_coronal = ImageTk.PhotoImage(img)
                self.canvas_coronal.delete(tk.ALL)
                self.canvas_coronal.create_image(self.offset_coronal_x,self.offset_coronal_y,anchor=tk.NW,image=self.img_tk_coronal)
            else:
                factor_w = self.spacing_y / min_spacing
                factor_h = self.spacing_z / min_spacing
                nuevo_w = max(1, int(w * self.zoom_sagital * factor_w))
                nuevo_h = max(1, int(h * self.zoom_sagital * factor_h))
                img = img.resize((nuevo_w, nuevo_h))
                self.img_tk_sagital = ImageTk.PhotoImage(img)
                self.canvas_sagital.delete(tk.ALL)
                self.canvas_sagital.create_image(self.offset_sagital_x,self.offset_sagital_y,anchor=tk.NW,image=self.img_tk_sagital)

    def Cambiar_slice_axial(self, valor):
        self.slice_axial = int(float(valor))
        self.dibujar(vista="axial")
    def Cambiar_slice_coronal(self, valor):
        self.slice_coronal = int(float(valor))
        self.dibujar(vista="coronal")
    def Cambiar_slice_sagital(self, valor):
        self.slice_sagital = int(float(valor))
        self.dibujar(vista="sagital")

    def Normalizar_imagen(self,img):
        img = img.astype(np.float32)
        minimo = img.min()
        maximo = img.max()
        if maximo - minimo == 0:
            return np.zeros_like(img, dtype=np.uint8)
        img = (img - minimo) / (maximo - minimo)
        return (img * 255).astype(np.uint8)

    def Get_volumen_actual(self):
        """
        Devuelve el volumen 3D (Z, Y, X) sobre el que se calculan los cortes.
        Si la imagen es 4D, devuelve el volumen correspondiente al instante
        de tiempo actualmente seleccionado (self.slice_tiempo).
        """
        if self.array_imagen is None:
            return None
        if self.es_4d:
            indice = min(self.slice_tiempo, self.array_imagen.shape[0] - 1)
            return self.array_imagen[indice]
        return self.array_imagen

    def Get_imagen_actual(self,vista:str=None):
        try:
            if vista:
                volumen = self.Get_volumen_actual()
                if volumen is None:
                    img = np.zeros((512, 512), dtype=np.uint8)
                    return Image.fromarray(img)

                if vista == "axial":
                    img = volumen[self.slice_axial, :, :]
                elif vista == "coronal":
                    img = volumen[:, self.slice_coronal, :]
                    img = np.flipud(img)
                else:
                    img = volumen[:, :, self.slice_sagital]
                    img = np.flipud(img)
                img = self.Normalizar_imagen(img)
                return Image.fromarray(img)
        except Exception as e:
            log.error(f"Error en la obtencion del corte de la imagen:\n{e}")


    def slider_visor(self):
        try:
            self.slider_axial = tk.Scale(self.frame_axial,from_=0, to=self.maximo_axial,label="Axial".upper(), orient=HORIZONTAL,command=self.Cambiar_slice_axial,font=(" ", 7, "bold"),cursor="fleur",bg="#8C0000")
            self.slider_coronal = tk.Scale(self.frame_coronal, from_=0, to=self.maximo_coronal, label="Coronal".upper(),orient=HORIZONTAL,command=self.Cambiar_slice_coronal,font=(" ", 7, "bold"),cursor="fleur",bg="#8C8C00")
            self.slider_sagital = tk.Scale(self.frame_sagital, from_=0, to=self.maximo_sagital, label="Sagital".upper(),orient=HORIZONTAL,command=self.Cambiar_slice_sagital,font=(" ", 7, "bold"),cursor="fleur",bg="#00668C")

            self.slider_axial.pack(side=tk.TOP, fill=tk.X,padx=5)
            self.slider_coronal.pack(side=tk.TOP, fill=tk.X,padx=5)
            self.slider_sagital.pack(side=tk.TOP, fill=tk.X,padx=5)

            self.slider_axial.set(self.slice_axial)
            self.slider_coronal.set(self.slice_coronal)
            self.slider_sagital.set(self.slice_sagital)
        except Exception as e:
            log.error(f"Error: \n{e}")

    def Cargar_nueva_imagen(self,imagen:str=None):
        self.imagen=imagen
        if self.imagen:
            self.Obtencion_imagen()
            self.slider_axial.configure(to=self.maximo_axial)
            self.slider_coronal.configure(to=self.maximo_coronal)
            self.slider_sagital.configure(to=self.maximo_sagital)
            self.slider_axial.set(self.slice_axial)
            self.slider_coronal.set(self.slice_coronal)
            self.slider_sagital.set(self.slice_sagital)
            self.dibujar("axial")
            self.dibujar("coronal")
            self.dibujar("sagital")

