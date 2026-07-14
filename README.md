# MedicalOmni3D

MedicalOmni3D es una aplicación de escritorio desarrollada en **Python** para facilitar la segmentación semiautomática y la visualización tridimensional de estructuras 3D.

La aplicación integra modelos de **Inteligencia Artificial** basados en  **[nnU-Net](https://github.com/MIC-DKFZ/nnUNet)**, permitiendo generar segmentaciones automáticas a partir de estudios de tomografía computarizada (CT), además de ofrecer herramientas para la visualización y exportación de modelos 3D.

---

# Características

* Inicio de sesión mediante autenticación de usuario.
* Importación de imágenes médicas en formato **NIfTI (.nii.gz)**.
* Segmentación automática utilizando modelos entrenados con **nnU-Net**.
* Comunicación con un servidor **MONAI Label** para realizar la inferencia.
* Visualización multiplanar (axial, coronal y sagital).
* Reconstrucción tridimensional de las estructuras segmentadas.
* Exportación de modelos segmentados.
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
* MONAI Label
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
git clone https://github.com/Andresf-Asprilla/Modelo-segmentacion-APCIVMAPCAs.git
```

```bash
cd Modelo-segmentacion-APCIVMAPCAs
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

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Ejecución

```bash
python App_medicalomni3d.py
```

---

# Flujo de trabajo

1. Iniciar sesión en la aplicación.
2. Seleccionar el estudio de tomografía en formato **NIfTI (.nii.gz)**.
3. Enviar el estudio al servidor MONAI Label.
4. Ejecutar la segmentación automática.
5. Visualizar el resultado en 2D y 3D.
6. Exportar la segmentación.

---

# Modelo de Inteligencia Artificial

La aplicación utiliza un modelo basado en **nnU-Net v2** entrenado específicamente para segmentar:

* MAPCAs del lado derecho.
* MAPCAs del lado izquierdo.
* Arteria pulmonar.
* Aorta.

El modelo fue desarrollado utilizando estudios tomográficos pediátricos anonimizados y optimizado para obtener una segmentación rápida y precisa.

---

# Formatos soportados

## Entrada

* `.nii`
* `.nii.gz`

## Salida

* `.nrrd`
* `.stl`
* `.obj` *(si está habilitado)*
* `.ply` *(opcional)*

---

# Capturas de pantalla

Puedes agregar imágenes como las siguientes:

```text
docs/images/login.png

docs/images/main_window.png

docs/images/segmentation.png

docs/images/3d_view.png
```

Luego referenciarlas:

```markdown
## Inicio de sesión

![Login](docs/images/login.png)

## Segmentación

![Segmentación](docs/images/segmentation.png)

## Visualización 3D

![3D](docs/images/3d_view.png)
```

---

# Contribuciones

Las contribuciones son bienvenidas.

1. Crear un Fork.
2. Crear una nueva rama.

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realizar los cambios.

4. Enviar un Pull Request.

---

# Autor

**Andrés Felipe Asprilla Mosquera**

Ingeniero Biomédico

Universidad EIA

---

# Licencia

Este proyecto está disponible únicamente con fines académicos e investigativos. Cualquier uso comercial requiere autorización del autor.

---

# Contacto

GitHub: **[https://github.com/Andresf-Asprilla](https://github.com/Andresf-Asprilla)**

Correo electrónico: **(Agregar correo institucional o personal)**

---

## Cita

Si utilizas MedicalOmni3D en investigaciones académicas, por favor cita el proyecto y el trabajo de grado correspondiente.
