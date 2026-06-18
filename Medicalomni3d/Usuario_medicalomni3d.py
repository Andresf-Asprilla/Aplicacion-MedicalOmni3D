class Usuario:
    Rol=["Usuario", "Administrador"]
    Estado=["Bloqueado","Desbloqueado"]
    ACCIONES = ["Inicio de sesión","Inicio de sesión Fallido","Cierre de sesión","Importó imagen","Eliminó imagen","Exportó imagen","Ejecutó modelo","Creó usuario","Editó usuario","Eliminó usuario","Cambió configuración del sistema"]
    def __init__(self,id_usuario:int=None,username:str=None,password:str=None,rol:str=None,bloqueado:str=None,intentos_fallidos:str=None,fecha:str=None,accion:str=None):
        self.__id_usuario=id_usuario
        self.__username=username
        self.__password=password
        self.__rol=rol
        self.__intentos_fallidos=intentos_fallidos
        self.__bloqueado=bloqueado
        self.__fecha=fecha
        self.__accion = accion

    @property
    def id_usuario(self):
        return self.__id_usuario

    @property
    def accion(self):
        return self.__accion
    @property
    def username(self):
        return self.__username
    @property
    def password(self):
        return self.__password
    @property
    def rol(self):
        return self.__rol
    @property
    def bloqueado(self):
        return self.__bloqueado
    @property
    def intentos_fallidos(self):
        return self.__intentos_fallidos
    @property
    def fecha(self):
        return self.__fecha
    @username.setter
    def username(self, renombre):
        self.__username=renombre
    @password.setter
    def password(self,newpassword):
        self.__password=newpassword
    @rol.setter
    def rol(self, nuevo_rol):
        self.__rol=nuevo_rol
    @intentos_fallidos.setter
    def intentos_fallidos(self,nuevo_intento):
        self.__intentos_fallidos=nuevo_intento
    @fecha.setter
    def fecha(self, nueva_fecha):
        self.__fecha=nueva_fecha

    @bloqueado.setter
    def bloqueado(self, nuevo_estado):
        self.__bloqueado=nuevo_estado
    @accion.setter
    def accion(self, nueva_accion):
        self.__accion = nueva_accion
    def __str__(self):
        return f"-Rol:{self.rol}\n-Nombre Usuario:{self.username}\n-Contraseña:{self.password}"
