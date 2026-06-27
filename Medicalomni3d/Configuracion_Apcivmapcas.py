import os, sys, threading, subprocess,torch, requests, time, zipfile, shutil, platform,keyring
from tkinter import ttk,messagebox
import nibabel as nib
from Medicalomni3d.loggin_MedicalOmni3d import  log
from cryptography.fernet import Fernet
from Medicalomni3d.Configuracion_medicalomni3d import Configuracion_ventana
import tkinter as tk
from platformdirs import PlatformDirs
import SimpleITK as sitk
import numpy as np
import json

basedir = os.path.dirname(__file__)


class Configuracionnnunetv2:
    _dir_app=PlatformDirs(appname="MedicalOmni3D", appauthor=False)
    PATH_BASE_APP = _dir_app.user_data_dir
    PATH_LOGGING=_dir_app.user_log_dir
    PATH_CONFIGURACION=_dir_app.user_config_dir
    BASE_LOGGING=os.path.join(PATH_CONFIGURACION,"loggin_MedicalOmni3D")
    BASE_CONFIGURACION=os.path.join(PATH_CONFIGURACION,"configuracion_MedicalOmni3D.json")
    BASE_DIR = os.path.join(PATH_BASE_APP, "Configuracion_MedicalOmni3D")
    BASE_DIR2 = os.path.join(PATH_BASE_APP, "Base_Datos_MedicalOmni3D")
    TIPO_EXTENSION = {"NIfTI": ".nii.gz", "NRRD": ".nrrd", "MINC": ".mnc", "TIFF": ".tif"}
    ARCHIVO_JSON = ['dataset.json', 'plans.json', 'predict_from_raw_data_args.json']
    DEVICE = {"Windows":"cuda", "Darwin":"mps", "Linux":"cuda"}
    PATH_DICT = {
        "nnUNet_raw": os.path.join(BASE_DIR, "nnUNet_raw"),
        "nnUNet_preprocessed": os.path.join(BASE_DIR, "nnUNet_preprocessed"),
        "nnUNet_results": os.path.join(BASE_DIR, "nnUNet_results"),
        "RAW_DATA_PATH": os.path.join(BASE_DIR, "RawData"),
        "nnUNet_Almacenamiento_imagenes": os.path.join(BASE_DIR, "nnUNet_Almacenamiento_imagenes"),
        "nnUNet_Procesamiento_imagenes": os.path.join(BASE_DIR, "nnUNet_Procesamiento_imagenes"),
        "nnUNet_Salida_imagenes_modelo": os.path.join(BASE_DIR, "nnUNet_Salida_imagenes_modelo"),
        "Base_Datos_MedicalOmni3D": BASE_DIR2,
        "Configuracion_medicalomni":os.path.dirname(BASE_CONFIGURACION)
    }
    BANDERA_IMPORTACION=True
    BANDERA_TERMINAR_BARRA=False
    @classmethod
    def Creacion_carpetas(cls, folder_path, overwrite=False):
        try:
            print(f"Intentando crear: {folder_path}")

            if os.path.exists(folder_path):

                if not overwrite:
                    print(f"{folder_path} existe")
                else:
                    print(f"{folder_path} será sobrescrita")
                    shutil.rmtree(folder_path)
                    os.makedirs(folder_path)

            else:
                os.makedirs(folder_path)
                print(f"{folder_path} creada correctamente")

        except Exception as e:
            log.critical(
                f"Error: No se pudieron crear las carpetas:\n{e}"
            )


    @classmethod
    def Creacion_variables_entorno(cls):
        try:
            os.makedirs(cls.PATH_CONFIGURACION, exist_ok=True)
            os.makedirs(cls.PATH_LOGGING, exist_ok=True)
            for env_var, path in cls.PATH_DICT.items():
                os.environ[env_var] = path
                cls.Creacion_carpetas(path, overwrite=False)
        except Exception as e:
            log.error(f"Error: No se pudieron crear las  variables de entorno :\n{e}")

    @classmethod
    def Buscar_archivo(cls, zip_path: str = "") -> str:
        try:
            return [j for j in os.listdir(cls.BASE_DIR) if j.startswith(zip_path)][0]
        except Exception as e:
            log.error("No se encontro el archivo a descargar: ", e)

    @classmethod
    def Configuracion_apcivmapcas_json(cls):
        config_model = {"modelos": {}, "tipo_archivo_ex": "NIfTI", "path_import_imagen": "", "path_import_modelo": "",
                        "path_export_imagen": "", "modelo_seleccionado": ""}
        try:
            archivojson = cls.BASE_CONFIGURACION
            if os.path.exists(archivojson):
                with open(archivojson, "r") as archivo_j:
                    config_model = json.load(archivo_j)
                return config_model
            else:
                with open(archivojson, "w") as f:
                    json.dump(config_model, f, indent=4)
                return config_model
        except Exception as e:
            log.error(f"Error en la configuracion del archivo json:\n{e}")
            #return config_model

    @classmethod
    def Configuracion_importacion_modelo_json(cls, name_model: str = ""):
        try:
            archivos = [
                os.path.join(cls.PATH_DICT["nnUNet_results"], archivo)
                for archivo in os.listdir(cls.PATH_DICT["nnUNet_results"])
                if not archivo.endswith(".json")
            ]
            carpeta_dataset = max(archivos, key=os.path.getmtime)

            if len(os.listdir(carpeta_dataset)) == 1:
                ruta_modelo3 = os.listdir(carpeta_dataset)[0]
                entrenamiento_model, _, tipo_modelo = ruta_modelo3.split("__")
                fold_modelo = []
                for fold in os.listdir(os.path.join(carpeta_dataset, ruta_modelo3)):
                    if fold.startswith("fold") and fold.split("_")[-1].isdigit():
                        fold_modelo.append(fold.split("_")[-1])

                if not fold_modelo:
                    messagebox.showerror(
                        title="Error en la importación del modelo",
                        message="No se encontraron los archivos fold en el modelo"
                    )
                    shutil.rmtree(cls.ruta_dataset)
                    cls.BANDERA_IMPORTACION = False
                else:
                    archivojson = cls.BASE_CONFIGURACION
                    config_default = {
                        "modelos": {},
                        "tipo_archivo_ex": "NIfTI",
                        "path_import_imagen": "",
                        "path_import_modelo": "",
                        "path_export_imagen": "",
                        "modelo_seleccionado": ""
                    }

                    if os.path.exists(archivojson):
                        try:
                            with open(archivojson, "r") as archivo_j:
                                config_model = json.load(archivo_j)
                            if "modelos" not in config_model:
                                config_model["modelos"] = {}
                        except (json.JSONDecodeError, Exception) as e:
                            log.error(f"JSON corrupto, usando configuración por defecto: {e}")
                            config_model = config_default
                    else:
                        config_model = config_default

                    config_model["modelos"][name_model] = {
                        "dataset": os.path.basename(carpeta_dataset),
                        "trainer": entrenamiento_model,
                        "modelo": tipo_modelo,
                        "fold": fold_modelo,
                        "path_desinstalar": carpeta_dataset,
                        "Normalizacion": True,
                        "Espaciado": True,
                        "nuevo_espaciado": [1, 1, 1],
                        "device": cls.Dispositivo_inferencia()[0]
                    }

                    with open(archivojson, "w") as f:
                        json.dump(config_model, f, indent=4)
                        f.flush()
                        os.fsync(f.fileno())

                    log.info(f"Modelo '{name_model}' guardado correctamente en JSON")

            else:
                messagebox.showerror(
                    title="Error en la importación del modelo",
                    message="Para hacer uso de esta aplicacion debe haber un solo entrenamiento por modelo"
                )
                cls.BANDERA_IMPORTACION = False
                shutil.rmtree(cls.ruta_dataset)

        except Exception as e:
            log.error(f"Error: En la configuracion del modelo {name_model}:\n {e}")
            cls.BANDERA_IMPORTACION = False
    @classmethod
    def Importacion_modelo(cls, path_model: str = "") -> None:
        try:
            archivojson = cls.BASE_CONFIGURACION
            config_default = {
                "modelos": {},
                "tipo_archivo_ex": "NIfTI",
                "path_import_imagen": "",
                "path_import_modelo": "",
                "path_export_imagen": "",
                "modelo_seleccionado": ""
            }
            try:
                with open(archivojson, "r") as archivo_j:
                    config_model = json.load(archivo_j)
            except json.JSONDecodeError:
                with open(archivojson, "w") as f:
                    json.dump(config_default, f, indent=4)
                config_model = config_default
            if os.path.isfile(path_model):
                with zipfile.ZipFile(path_model, 'r') as zip_ref:
                    nombres = zip_ref.namelist()
                    carpeta_principal = nombres[0].split("/")[0]
                    cls.ruta_dataset = os.path.join(cls.PATH_DICT["nnUNet_results"], carpeta_principal)
                    modelo_existente = None
                    for nombre_modelo, info_modelo in config_model["modelos"].items():
                        if info_modelo["dataset"] == carpeta_principal:
                            modelo_existente = nombre_modelo
                            break

                    if os.path.exists(cls.ruta_dataset):
                        messagebox.showerror(title="Error en la importación del modelo",message=f"El dataset '{os.path.basename(cls.ruta_dataset)}' ya se encuentra registrado en la aplicación. La importación ha sido cancelada.")
                        cls.BANDERA_IMPORTACION = False
                        return

                    name_model = os.path.basename(path_model).split(".")[0]

                    if name_model not in config_model["modelos"].keys():
                        zip_ref.extractall(cls.PATH_DICT["nnUNet_results"])
                        cls.Configuracion_importacion_modelo_json(name_model)
                    else:
                        messagebox.showinfo(title="Error importación del modelo",message=f"El modelo '{name_model}' ya existe en la aplicación. Para volver a importarlo, primero elimine el modelo actual y luego inténtelo nuevamente.")
                        cls.BANDERA_IMPORTACION = False
            else:

                messagebox.showinfo(title="Error importación del modelo",message=f"ZIP no encontrado: {path_model}")
                cls.BANDERA_IMPORTACION = False

        except Exception as e:
            import traceback
            log.error(f"Error en la importación del modelo:\n{e}")
            cls.BANDERA_IMPORTACION = False

    @classmethod
    def ventana_importar_modelo(cls, master, path_model: str, callback=None):
        cls.BANDERA_IMPORTACION = True
        ventana = tk.Toplevel(master)
        Configuracion_ventana(ventana=ventana, ancho=350, alto=100, titulo="Importación de Modelo...",
                              no_modificar=True)
        try:
            sistema = platform.system()
            if sistema == "Windows":
                ventana.iconbitmap(os.path.join(basedir, "Assets", "medicalomni3d.ico"))
            else:
                icon_img = Image.open(os.path.join(basedir, "Assets", "medicalomni3d.png"))
                icon_photo = ImageTk.PhotoImage(icon_img)
                ventana._icon_photo = icon_photo
                ventana.iconphoto(True, icon_photo)
        except Exception:
            pass

        ventana.transient(master)
        ventana.protocol("WM_DELETE_WINDOW", lambda: None)
        ventana.focus()
        ttk.Label(ventana, text="Importando modelo, por favor espere...").pack(pady=10)
        progreso = ttk.Progressbar(ventana, mode="indeterminate", length=280)
        progreso.pack(pady=5)
        ventana.update()
        ventana.update_idletasks()
        progreso.start(12)
        ventana.grab_set()
        ventana.focus()

        hilo = threading.Thread(target=cls.Importacion_modelo, args=(path_model,), daemon=True)
        hilo.start()
        cls.monitorear_importacion(ventana, progreso, hilo, callback, master=master)

    @classmethod
    def monitorear_importacion(cls, ventana, progreso, hilo,callback,master):
        if hilo.is_alive():
            ventana.after(100,lambda: cls.monitorear_importacion(ventana,progreso,hilo,callback,master))
            if not cls.BANDERA_IMPORTACION:
                ventana.destroy()
        else:
            progreso.stop()
            if ventana.winfo_exists():
                ventana.grab_release()
                ventana.destroy()
                if callback:
                    callback()
            if cls.BANDERA_IMPORTACION:
                messagebox.showinfo(title="Exito en importación del modelo",message=f"Sea importado el modelo de manera exitosa")

                master.focus()

    @classmethod
    def Codificacion_imagenes(cls, lista_imagenes_selecionadas: list = None) -> tuple:
        try:
            if len(lista_imagenes_selecionadas) > 0:
                diccionario_path = {}
                idx = 0
                for nombre_archivo in os.listdir(cls.PATH_DICT["nnUNet_Almacenamiento_imagenes"]):
                    nombre_archivo=".".join(nombre_archivo.split(".", maxsplit=-2)[:3])
                    if nombre_archivo in lista_imagenes_selecionadas:
                        input_path_file = os.path.join(cls.PATH_DICT["nnUNet_Almacenamiento_imagenes"], nombre_archivo)
                        input_temp_model_file = os.path.join(cls.PATH_DICT["nnUNet_Procesamiento_imagenes"],f"paciente_{idx:03d}_0000.nii.gz")
                        out_temp_model_file = os.path.join(cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"],f"paciente_{idx:03d}.nii.gz")
                        path_file_delete = os.path.join(cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"], nombre_archivo)
                        diccionario_path[nombre_archivo] = {"input_path": input_path_file,"input_temp_model": input_temp_model_file,"file_delete": path_file_delete,"out_temp_model": out_temp_model_file}
                        idx += 1
                return diccionario_path
            else:
                messagebox.showerror(title="Error en la codificación", message="Seleccione al menos una imagen")
                return False
        except Exception as e:
            log.error(f"Error: En la codificación de las imagenes:\n{e}")

    @classmethod
    def Verification_archivos(cls) -> bool:
        try:
            nombre_imagenes = os.listdir(cls.PATH_DICT["nnUNet_Almacenamiento_imagenes"])
            verificador_type_file = np.array([j.endswith((".nii.gz", ".nii")) for j in nombre_imagenes])
            if len(verificador_type_file) != 0:
                if verificador_type_file.all():
                    verificador_type_file = True
                else:
                    verificador_type_file = False
                    log.error("Se enconrto almenos una imagen que no cumple el formato nifti")
            else:
                log.error("En la Carpeta no se encuentran las imagenes o no estan en el formato adecuado")
                verificador_type_file = None
            return verificador_type_file
        except Exception as e:
            log.error(f"Error: En la verificacion  de los archivos:\n{e}")

    @classmethod
    def Obtener_espaciado_original(cls, lista_imagenes_selecionadas: list = None) -> dict:
        try:
            if len(lista_imagenes_selecionadas) > 0:
                espaciados = {}
                for archivo_img in lista_imagenes_selecionadas:
                    archivo_img=archivo_img
                    img = sitk.ReadImage(os.path.join(cls.PATH_DICT["nnUNet_Almacenamiento_imagenes"], archivo_img))
                    espaciados[archivo_img] = {
                        "spacing": img.GetSpacing(),
                        "origin": img.GetOrigin(),
                        "direction": img.GetDirection()
                    }
                return espaciados
            else:
                messagebox.showerror(title="Error obtener espaciado", message="Seleccione al menos una imagen")
                return None
        except Exception as e:
            log.critical(f"Error: En La obtencion del espaciado de la imagenes:\n{e}")
            return None

    @classmethod
    def Nuevo_espaciado(cls, diccionario_codificado: dict = None, nuevo_espaciado=None,
                        normalization: bool = False) -> None:
        try:
            if nuevo_espaciado is None:
                nuevo_espaciado = [1, 1, 1]
            for diccionario_path_codificado in diccionario_codificado.values():
                if normalization:
                    imagen = sitk.ReadImage(diccionario_path_codificado['input_temp_model'])
                    imagen.SetSpacing(nuevo_espaciado)
                    sitk.WriteImage(imagen, diccionario_path_codificado['input_temp_model'])
                else:
                    imagen = sitk.ReadImage(diccionario_path_codificado['input_path'])
                    imagen.SetSpacing(nuevo_espaciado)
                    sitk.WriteImage(imagen, diccionario_path_codificado['input_temp_model'])
        except Exception as e:
            log.critical(f"Error: Al establecer un espacioado de {nuevo_espaciado} a las imagenes:\n {e}")

    @classmethod
    def Normalizacion(cls, diccionario_codificado) -> dict:
        try:
            for diccionario_path_codificado in diccionario_codificado.values():
                imagen = sitk.ReadImage(diccionario_path_codificado['input_path'])
                imagen_float = sitk.Cast(imagen, sitk.sitkFloat32)
                sitk.WriteImage(sitk.RescaleIntensity(imagen_float, 0, 1),
                                diccionario_path_codificado['input_temp_model'])
        except Exception as e:
            log.critical(f"Error:En la normalizacion de las imagenes:\n{e}")

    @classmethod
    def Eliminarcion(cls, lista_imagenes_selecionadas: list = None, diccionario_paths: dict = None) -> None:
        try:
            if len(lista_imagenes_selecionadas) > 0:
                for imagen_selecionada in lista_imagenes_selecionadas:
                    path_almacenamiento = diccionario_paths[imagen_selecionada]["input_path"]+".enc"
                    path_salida = diccionario_paths[imagen_selecionada]["file_delete"]
                    if os.path.exists(path_almacenamiento):
                        os.remove(path_almacenamiento)
                    if os.path.exists(path_salida):
                        os.remove(path_salida)
        except Exception as e:
            log.error(f"Error: En eliminacion de la siguiente imagen:\n{e}")

    @classmethod
    def Restaurar_espaciado_original(cls, diccionario_paths: dict = None, diccionario_spacings: dict = None,espaciado: bool = False) -> None:
        try:
            for nombre_imagenes in diccionario_paths.keys():
                imagen = sitk.ReadImage(diccionario_paths[nombre_imagenes]['out_temp_model'])
                if espaciado:
                    info = diccionario_spacings[nombre_imagenes]
                    imagen.SetSpacing(info["spacing"])
                    imagen.SetOrigin(info["origin"])
                    imagen.SetDirection(info["direction"])
                sitk.WriteImage(imagen, os.path.join(cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"], nombre_imagenes))
                os.remove(diccionario_paths[nombre_imagenes]['out_temp_model'])
                os.remove(diccionario_paths[nombre_imagenes]['input_temp_model'])
            cls.Eliminacion_json_salida()
        except Exception as e:
            log.critical(f"Error: En restablecer el espaciado:\n {e}")

    @classmethod
    def Exportacion_imagenes(cls, tipo_extension: str = "", lista_imagenes_selecionadas: list = None,
                             path_exportacion: str = "", diccionario_paths: dict = None) -> None:
        try:
            os.makedirs(path_exportacion, exist_ok=True)
            if len(lista_imagenes_selecionadas) > 0 and tipo_extension != "":
                mensaje_panatalla_falla=False
                mensaje_panatalla_correcto = False
                lista_imagenes_no_export=[]
                lista_imagenes_export = []
                for clave in lista_imagenes_selecionadas:
                    path_imagen = diccionario_paths[clave]["file_delete"]
                    nombre_imagen=os.path.basename(path_imagen)
                    if  nombre_imagen in os.listdir(cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"]):
                        mensaje_panatalla_correcto = True
                        lista_imagenes_export.append(nombre_imagen.split(".")[-3])
                        nombre_imagen = os.path.basename(path_imagen).split(".")[-3]
                        extension = cls.TIPO_EXTENSION[tipo_extension]
                        imagen_exportar = "".join([nombre_imagen, extension])
                        imagen = sitk.ReadImage(path_imagen)
                        sitk.WriteImage(imagen, os.path.join(path_exportacion, imagen_exportar))
                    else:
                        mensaje_panatalla_falla=True
                        lista_imagenes_no_export.append(nombre_imagen.split(".")[-3])
                if mensaje_panatalla_correcto:
                    text = ",".join(lista_imagenes_export)
                    messagebox.showinfo(title="Exportación",
                                         message=f"La siguiente imagen se exportó correctamente:\n{text}")
                if mensaje_panatalla_falla:
                    text = ",".join(lista_imagenes_no_export)
                    messagebox.showerror(title="Error Exportación", message=f"No se pudo exportar la siguiente imagen:\n{text}")


        except Exception as e:
            log.error(f"Error: Importacion de la imagenes :\n{e}")

    @classmethod
    def Dispositivo_inferencia(cls) -> str:
        try:
            sistema = platform.system()
            lista_dispositivos=[]
            if cls.DEVICE[sistema]=="cuda":
                if torch.cuda.is_available():
                    lista_dispositivos.append("cuda")
            else:
                if torch.mps.is_available():
                    lista_dispositivos.append("mps")
            if torch.cpu.is_available():
                lista_dispositivos.append("cpu")
            return lista_dispositivos
        except Exception as e:
            log.critical(f"Error: En la determinacion del dispositivo:\n{e}")
            return None

    @classmethod
    def Eliminacion_json_salida(cls) -> None:
        try:
            if os.path.exists(cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"]):
                for json in cls.ARCHIVO_JSON:
                    json_eliminar = os.path.join(cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"], json)
                    if os.path.exists(json_eliminar):
                        os.remove(json_eliminar)
        except Exception as e:
            log.error(f"Error: En la eliminacion de los archivos json:\n{e}")
    @classmethod
    def Obtencion_plan_modelo(cls,dataset):
        path=os.path.join(cls.PATH_DICT["nnUNet_results"],dataset)
        if os.path.exists(path):
            if len(os.listdir(path))==1:
                archivo=os.listdir(path)[0]
                path_json=os.path.join(path,archivo,"plans.json")
                if os.path.isfile(path_json):
                    with open(path_json,"r") as plant:
                        contenido=json.load(plant)
                    if "plans_name" in contenido.keys():
                        return contenido["plans_name"]
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None
    @classmethod
    def Inferencias_modelo_asincrona(cls, modelo_selecionado: str = "", device: str = None):
        try:
            if device is not None:

                path_json = cls.BASE_CONFIGURACION
                if os.path.exists(path_json) and modelo_selecionado != "":
                    with open(path_json, "r") as archivo:
                        config = json.load(archivo)
                    inf_model = config["modelos"][modelo_selecionado]
                    plant_model=cls.Obtencion_plan_modelo(dataset=inf_model["dataset"])
                    if plant_model :
                        comando = ["nnUNetv2_predict","-d", inf_model["dataset"],"-i", cls.PATH_DICT["nnUNet_Procesamiento_imagenes"],"-o", cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"],"-f", *inf_model["fold"],"-tr", inf_model["trainer"],"-c", inf_model["modelo"],"-device", device,"-p",plant_model]
                        proceso_gpu = subprocess.Popen(comando)
                        return proceso_gpu
                    else:
                        log.critical(f"Error: No se puede ejecutar el modelo")
                        return None
        except Exception as e:
            log.critical(f"Error: al lanzar el subproceso nnUNet: {e}")
            return None

    @classmethod
    def Inferencias_modelo(cls, modelo_selecionado: str = "", device: str = None) -> None:
        try:
            if device is not None:
                path_json = cls.BASE_CONFIGURACION
                if os.path.exists(path_json) and modelo_selecionado != "":
                    with open(path_json, "r") as archivo:
                        config = json.load(archivo)
                    inf_model = config["modelos"][modelo_selecionado]
                    plant_model = cls.Obtencion_plan_modelo(dataset=inf_model["dataset"])
                    if plant_model:
                        comando = ["nnUNetv2_predict","-d", inf_model["dataset"],"-i", cls.PATH_DICT["nnUNet_Procesamiento_imagenes"],"-o", cls.PATH_DICT["nnUNet_Salida_imagenes_modelo"],"-f", *inf_model["fold"],"-tr", inf_model["trainer"],"-c", inf_model["modelo"],"-device", device,"-p",plant_model]
                        subprocess.run(comando, check=True)
                    else:
                        log.error("Error: No se puede ejecutar el modelo")
                else:
                    log.error("Error: Instala un modelo valido de nnUNet")
            else:
                log.critical("Error:No se puede ejecutar la inferencia del modelo en este dispotivo")

        except Exception as e:
            log.critical(f"Error: No se pudo realizar la inferencia con el modelo:\n{e}")
    @classmethod
    def Clave_cifrado_imagenes(cls):
        clave = keyring.get_password("MedicalOmni3D","clave_imagenes")
        if clave is None:
            clave = Fernet.generate_key().decode()
            keyring.set_password("MedicalOmni3D","clave_imagenes",clave)
        return Fernet(clave.encode())

    @classmethod
    def Cifrar_imagenes(cls,path_imagen:str=None):
        if path_imagen:
            fernet=cls.Clave_cifrado_imagenes()
            ruta_int=os.path.join(cls.PATH_DICT["nnUNet_Almacenamiento_imagenes"],os.path.basename(path_imagen))
            ruta_out=ruta_int + ".enc"
            with open(ruta_int, "rb") as f:
                datos = f.read()
            datos_cifrados = fernet.encrypt(datos)
            with open(ruta_out, "wb") as f:
                f.write(datos_cifrados)
            os.remove(ruta_int)

    @classmethod
    def Descifrar_imagenes(cls, path_imagen: str = None):
        if path_imagen:
            fernet = cls.Clave_cifrado_imagenes()
            ruta_int = path_imagen + ".enc"
            with open(ruta_int, "rb") as f:
                datos = f.read()
            datos_cifrados = fernet.decrypt(datos)
            with open(path_imagen, "wb") as f:
                f.write(datos_cifrados)
    @classmethod
    def Desinstalar_modelos(cls, modelo_selecionado: str = "") -> None:
        try:
            path_json = cls.BASE_CONFIGURACION
            if os.path.exists(path_json) and modelo_selecionado != "":
                with open(path_json, "r") as archivo:
                    config = json.load(archivo)
                path_desistalar = config["modelos"][modelo_selecionado]["path_desinstalar"]
                shutil.rmtree(path_desistalar)
                config["modelos"].pop(modelo_selecionado)
                config["modelo_seleccionado"]=""
                with open(path_json, "w") as f:
                    json.dump(config, f, indent=4)
        except Exception as e:
            log.error(f"Error: En la desinstalacion del modelo {modelo_selecionado}:\n {e}")

    @classmethod
    def Sin_Normalizacion_espaciado(cls, diccionario_codificado: dict = None) -> None:
        try:
            if len(diccionario_codificado) > 0 and diccionario_codificado is not None:
                for imageneseleccionada in diccionario_codificado.values():
                    imagen = sitk.ReadImage(imageneseleccionada["input_path"])
                    sitk.WriteImage(imagen, imageneseleccionada["input_temp_model"])
        except Exception as e:
            log.error(f"Error: En la importacion de las imagenes :\n{e}")

    @classmethod
    def Procesamiento_completo(cls, lista_codificada: list = None, Normalizacion: bool = False, Espaciado: bool = False,
                               nuevo_espacio: list = None) -> None:
        try:

            if Normalizacion and Espaciado:
                cls.Normalizacion(diccionario_codificado=lista_codificada)
                cls.Nuevo_espaciado(diccionario_codificado=lista_codificada, nuevo_espaciado=nuevo_espacio,
                                    normalization=Normalizacion)
            elif Normalizacion:
                cls.Normalizacion(lista_codificada)
            elif Espaciado:
                cls.Nuevo_espaciado(diccionario_codificado=lista_codificada, nuevo_espaciado=nuevo_espacio,
                                    normalization=Normalizacion)
            else:
                cls.Sin_Normalizacion_espaciado(diccionario_codificado=lista_codificada)

        except Exception as e:
            log.critical(f"Error: En los procesos de normalizacion y espaciado:\n {e}")



if __name__ == "__main__":
    Configuracionnnunetv2.Creacion_variables_entorno()
    #Configuracionnnunetv2.Dispositivo_inferencia()
    #Configuracionnnunetv2.Importacion_modelo(r"C:\Users\andre\Downloads\APCIVMAPCAs_3d_lowres2.zip")
    #Configuracionnnunetv2.Cifrar_imagenes(path_imagen=r"C:\Users\andre\OneDrive\Escritorio\imagen_prueba\CTACardio3.nii.gz")

