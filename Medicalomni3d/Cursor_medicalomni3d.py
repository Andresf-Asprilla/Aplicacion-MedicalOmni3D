from sqlite3 import connect
import os
from Medicalomni3d.Configuracion_Apcivmapcas import  Configuracionnnunetv2
class CursorSqlite3:
    def __init__(self):
        self.path_base_datos=os.path.join(Configuracionnnunetv2.BASE_DIR2,"medicalomni3d.db")
        self._connexion=None
        self._cursor=None
    def __enter__(self):
        self._connexion=connect(self.path_base_datos)
        self._cursor=self._connexion.cursor()
        return self._cursor
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self._connexion.rollback()
        else:
            self._connexion.commit()
        self._connexion.close()


