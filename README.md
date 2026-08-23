# MedicalOmni3D

MedicalOmni3D es una aplicación de escritorio desarrollada en **Python** para facilitar la segmentación semiautomática y la visualización 3D.

La aplicación integra modelos de **Inteligencia Artificial** basados en  **[nnU-Net](https://github.com/MIC-DKFZ/nnUNet)**, un marco robusto y autoajustable para la segmentación mediante redes neuronales basadas en la arquitectura U-Net.



[![Ver introducción de MedicalOmni3D](imagenes/img_intro.png)](imagenes/video_intro.mp4)
---

# Características

* Inicio de sesión mediante autenticación de usuario.
* Importación de imágenes médicas en formato **NIfTI (.nii.gz)**.
* Segmentación automática utilizando modelos entrenados con **nnU-Net**.
* Visualización multiplanar (axial, coronal y sagital).
* Reconstrucción tridimensional de las estructuras segmentadas.
* Exportación de reconstrucciones.
* Interfaz gráfica desarrollada con **Tkinter**.
* Compatible con Windows, macOS y Linux.

---

# Objetivo

MedicalOmni3D ha sido desarrollado principalmente con fines de investigación, educativos y experimentales. Su propósito es facilitar la visualización, el procesamiento y el análisis de imágenes médicas, así como apoyar el desarrollo, la evaluación y la integración de modelos de inteligencia artificial en entornos de investigación.

---

# Arquitectura

```text
                 Usuario
                    │
                    ▼
          Interfaz MedicalOmni3D
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
 Carga imágenes           Gestión usuarios
        │
        ▼
  Preprocesamiento
        │
        ▼
     Modelo nnU-Net
        │
        ▼
 Segmentación automática
        │
        ▼
 Postprocesamiento
        │
        ▼
 Visualización 3D
        │
        ▼
 Exportación resultados
```

---

# Tecnologías utilizadas

* Python 3.11+
* Tkinter
* nnU-Net v2
* PyTorch
* SimpleITK
* NumPy
* OpenCV
* Matplotlib
* VTK
* SQLite
* Pillow

---

# Requisitos

## Hardware

* Procesador Intel Core i5 o superior.
* 8 GB de RAM (16 GB recomendados).
* GPU NVIDIA compatible con CUDA (opcional para acelerar la inferencia).
* 5 GB de espacio disponible.

## Software

* Python 3.11
* CUDA (opcional)
* Git

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/Andresf-Asprilla/Aplicacion-MedicalOmni3D
```

```bash
cd Aplicacion-MedicalOmni3D
```

---

## 2. Crear un entorno virtual

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instalar las dependencias

Antes de instalar las dependencias del proyecto, instale la versión de **PyTorch** compatible con su sistema operativo y hardware (CPU o GPU) siguiendo las instrucciones de la página oficial:

https://pytorch.org/get-started/locally/

Una vez instalado PyTorch, ejecute el siguiente comando para instalar el resto de las dependencias:

```bash
pip install -r requirements.txt
```

---

# Ejecución

Para iniciar MedicalOmni3D, ejecute:

```bash
python App_medicalomni3d.py
```
---

# Credenciales de acceso

Utilice las siguientes credenciales para iniciar sesión en MedicalOmni3D:

- **Usuario:** `admin@medicalomni3d.com`
- **Contraseña:** `Admin123*`
---

# Flujo de trabajo

1. Iniciar sesión en la aplicación.
2. Seleccionar el estudio de tomografía en formato **NIfTI (.nii.gz)**.
3. Ejecutar la segmentación automática.
4. Visualizar el resultado en  3D.
5. Exportar la reconstrucciones.

---

# Modelo de Inteligencia Artificial

La aplicación utiliza un modelo basado en **nnU-Net v2** entrenado específicamente para segmentar:

* Lado derecho del Corazon.
* Lado izquierdo del Corazon.
* Arteria pulmonar.
* Aorta.



---

# Formatos soportados

## Entrada
* `.nii.gz`

## Salida

* `.nrrd`
* `.nii.gz`
* `.mnc` 
* `.tif` 
