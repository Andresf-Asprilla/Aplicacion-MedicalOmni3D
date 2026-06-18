import os
import sqlite3
from Medicalomni3d.loggin_MedicalOmni3d import log

class Conexion_Base_Datos_MedicalOmni3D:
    Ruta_base_datos=None
    Base_Datos_MedicalOmni3D="medicalomni3d.db"
    Tabla_Datos = {
    "usuarios": """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT DEFAULT 'Usuario',
        intentos_fallidos INTEGER DEFAULT 0,
        bloqueado INTEGER DEFAULT 0,
        fecha_bloqueo TEXT,
        fecha_ultimo_acceso TEXT DEFAULT 'No ha iniciado sesión'
    )""",

    "logs_acceso": """
    CREATE TABLE IF NOT EXISTS logs_acceso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        fecha TEXT,
        accion TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )"""
}

    connexion=None
    cursor=None

    @classmethod
    def Creacion_baseDatos(cls)->None:
        try:
            if cls.connexion is None:
                if cls.Ruta_base_datos is not None:
                    cls.connexion=sqlite3.connect(os.path.join(cls.Ruta_base_datos,cls.Base_Datos_MedicalOmni3D))
        except Exception as e:
            log.error(f"Error: En la creacion de la base de datos del programa:\n{e}")

    @classmethod
    def Creacion_Tablas(cls)->None:
        if cls.connexion is not None:
            cls.cursor=cls.connexion.cursor()
            cls.cursor.execute("PRAGMA foreign_keys = ON")
            for tabla in cls.Tabla_Datos.keys():
                cls.cursor.execute(cls.Tabla_Datos[tabla])
                cls.connexion.commit()
            cls.connexion.close()


if __name__=="__main__":
    Conexion_Base_Datos_MedicalOmni3D.Creacion_baseDatos()
    Conexion_Base_Datos_MedicalOmni3D.Creacion_Tablas()


