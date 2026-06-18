import time,bcrypt
import datetime
from Medicalomni3d.loggin_MedicalOmni3d import log
from Medicalomni3d.Cursor_medicalomni3d import CursorSqlite3
import  sqlite3
from Medicalomni3d.Configuracion_Apcivmapcas import Configuracionnnunetv2
from Medicalomni3d.Usuario_medicalomni3d import Usuario
from tkinter import messagebox

class DAOMedicalOmni3D:

    SELECCION_USUARIOS="SELECT id,username,rol,bloqueado,fecha_ultimo_acceso FROM usuarios"
    SELECCION_USUARIO_EDITAR= "SELECT id,username,rol,bloqueado,fecha_ultimo_acceso FROM usuarios WHERE id=?"
    SELECCION_USUARIOS_BUSCAR = "SELECT id,username,rol,bloqueado,fecha_ultimo_acceso FROM usuarios WHERE username LIKE ?"
    SELECCION_HISTORIAL_ACCESO_TODO="SELECT u.username,l.fecha,l.accion FROM usuarios u INNER JOIN logs_acceso l ON u.id=l.usuario_id"
    SELECCION_HISTORIAL_ACCESO_FILTRO_USUARIO="SELECT u.username,l.fecha,l.accion FROM usuarios u INNER JOIN logs_acceso l ON u.id=l.usuario_id WHERE u.username LIKE ?"
    SELECCION_HISTORIAL_ACCESO_FILTRO_ACCION="SELECT u.username,l.fecha,l.accion FROM usuarios u INNER JOIN logs_acceso l ON u.id=l.usuario_id WHERE l.accion LIKE ?"
    SELECCION_HISTORIAL_ACCESO_FILTRO_USUARIO_ACCION = "SELECT u.username,l.fecha,l.accion FROM usuarios u INNER JOIN logs_acceso l ON u.id=l.usuario_id WHERE u.username LIKE ? AND l.accion LIKE ?"
    INSERTAR_USUARIO="INSERT INTO usuarios (username,password_hash,rol,bloqueado,fecha_bloqueo) VALUES(?,?,?,?,?)"
    EDITAR_USUARIO_PASSWORD = "UPDATE usuarios SET username=?,password_hash=?,rol=?,bloqueado=? WHERE id=?"
    EDITAR_USUARIO = "UPDATE usuarios SET username=?,rol=?,bloqueado=? WHERE id=?"
    ELIMINAR_USUARIO="DELETE FROM usuarios WHERE id=?"
    CONSULTAR_USUARIO_CONTRASENA = "SELECT id,username,password_hash,rol,bloqueado,fecha_bloqueo FROM usuarios WHERE username=?"
    CONSULTAR_INTENTOS_FALLIDOS_BLOQUEO="SELECT id,intentos_fallidos,bloqueado,fecha_bloqueo FROM usuarios WHERE username=?"
    ACTUALIZAR_INTENTOS_FALLIDOS_BLOQUEO="UPDATE usuarios SET intentos_fallidos=?,bloqueado=? WHERE id=? "
    ACTUALIZAR_INTENTOS_FALLIDOS_BLOQUEO_FECHA="UPDATE usuarios SET intentos_fallidos=?,bloqueado=?,fecha_bloqueo=? WHERE id=? "
    ACTUALIZAR_INTENTOS_FALLIDOS = "UPDATE usuarios SET intentos_fallidos=? WHERE id=? "
    ACTUALIZAR_ULTIMA_SESION="UPDATE usuarios SET fecha_ultimo_acceso=? WHERE id=?"
    REGISTRAR_INTENTO="INSERT INTO logs_acceso (usuario_id,fecha,accion) VALUES(?,?,?)"

    SALT = bcrypt.gensalt()

    @classmethod
    def Seleccion_usuarios_buscar(cls,texto):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.SELECCION_USUARIOS_BUSCAR,(f"%{texto}%",))
                registro = Cursor.fetchall()
                if registro is None:
                    return None
                usuarios = [Usuario(id_usuario=usuario[0], username=usuario[1], rol=usuario[2], bloqueado=usuario[3],
                                    fecha=usuario[4]) for usuario in registro]
                return usuarios
        except Exception as e:
            log.error(f"Error no se puede acceder a la informacion de los usuarios:\n{e} ")

    @classmethod
    def Crear_usuario_admin_defecto(cls):
        try:
            usuarios = DAOMedicalOmni3D.Seleccion_usuarios()
            if not usuarios:
                user = Usuario(username="admin@medicalomni3d.com",password="Admin123*",rol="Administrador",intentos_fallidos=0,bloqueado=0)
                DAOMedicalOmni3D.Insertar_usuario(user)

        except Exception as e:
            log.error(f"Error al crear el usuario administrador por defecto:\n{e}")

    @classmethod
    def Seleccion_usuarios(cls):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.SELECCION_USUARIOS)
                registro = Cursor.fetchall()
                if registro is None:
                    return None
                usuarios = [Usuario(id_usuario=usuario[0], username=usuario[1], rol=usuario[2], bloqueado=usuario[3],
                                    fecha=usuario[4]) for usuario in registro]
                return usuarios
        except Exception as e:
            log.error(f"Error no se puede acceder a la informacion de los usuarios:\n{e} ")

    @classmethod
    def Seleccion_usuario_editar(cls,usuario:Usuario):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.SELECCION_USUARIO_EDITAR,(usuario.id_usuario,))
                registro = Cursor.fetchone()
                if registro is None:
                    return None
                usuarios = Usuario(id_usuario=registro[0], username=registro[1],rol=registro[2], bloqueado=registro[3],fecha=registro[4])
                return usuarios
        except Exception as e:
            log.error(f"Error no se puede acceder a la informacion de los usuarios:\n{e} ")

    @classmethod
    def Seleccion_historial_acceso(cls,usuario:str=None,accion:str=None):
        try:
            with CursorSqlite3() as Cursor:

                if usuario=="Todos" and accion=="Todos":
                    Cursor.execute(cls.SELECCION_HISTORIAL_ACCESO_TODO)
                elif usuario!="Todos" and accion=="Todos":
                    usuario = f"%{usuario}%"
                    Cursor.execute(cls.SELECCION_HISTORIAL_ACCESO_FILTRO_USUARIO,(usuario,))
                elif usuario=="Todos" and accion!="Todos":
                    accion=f"%{accion}%"
                    Cursor.execute(cls.SELECCION_HISTORIAL_ACCESO_FILTRO_ACCION,(accion,))
                else:
                    accion = f"%{accion}%"
                    usuario = f"%{usuario}%"
                    Cursor.execute(cls.SELECCION_HISTORIAL_ACCESO_FILTRO_USUARIO_ACCION,(usuario,accion))
                registro = Cursor.fetchall()
                if registro is None:
                    return None
                usuarios = [Usuario(fecha=usuario[1], username=usuario[0] , accion=usuario[2] ) for usuario in registro]
                return usuarios
        except Exception as e:
            log.error(f"Error no se puede acceder al historial de acceso:\n{e}")

    @classmethod
    def Insertar_usuario(cls, user:Usuario):
        try:
            with CursorSqlite3() as Cursor:
                if user.bloqueado:
                    user.fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    user.fecha=None
                Cursor.execute(cls.INSERTAR_USUARIO, (user.username,bcrypt.hashpw(user.password.encode('utf-8'),cls.SALT) , user.rol,user.bloqueado,user.fecha))
                return Cursor.rowcount

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror(title="Error al crear usuario",message="El usuario ingresado ya se encuentra registrado. Por favor, ingrese un nombre de usuario diferente.")
                return None
        except Exception:
            log.error(f"Error al agregar un nuevo usuario:\n{user}")


    @classmethod
    def Insertar_registro_intento(cls, user: Usuario,texto:str):
        try:
            with CursorSqlite3() as Cursor:
                user.fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                Cursor.execute(cls.REGISTRAR_INTENTO, (user.id_usuario, user.fecha,texto))
                return Cursor.rowcount
        except Exception:
            log.error(f"Error al registrar un nuevo intento de sesion:\n{user}")

    @classmethod
    def Editar_usuario_password(cls,user:Usuario):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.EDITAR_USUARIO_PASSWORD, (user.username, bcrypt.hashpw(user.password.encode('utf-8'), cls.SALT), user.rol, user.bloqueado, user.id_usuario))
                return Cursor.rowcount
        except Exception as e:
            log.error(f"Error al editar el usuario:\n{e}")
            return None

    @classmethod
    def Editar_usuario(cls, user: Usuario):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.EDITAR_USUARIO,(user.username, user.rol,user.bloqueado, user.id_usuario))
                return Cursor.rowcount
        except Exception as e:
            log.error(f"Error al editar el usuario:\n{e}")
    @classmethod
    def Eliminar_usuario(cls,user:Usuario):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.ELIMINAR_USUARIO,(user.id_usuario,))
                return Cursor.rowcount
        except Exception:
            log.error(f"Error al intentar eliminar al siguente usuario:\n{user}")

    @classmethod
    def Acceso_app(cls,user:Usuario):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.CONSULTAR_USUARIO_CONTRASENA,(user.username,))
                registro = Cursor.fetchone()
                if registro is None:
                    return None
                if bcrypt.checkpw(user.password.encode("utf-8"), registro[2]):
                    usuarios = Usuario(id_usuario=registro[0],username=registro[1],rol=registro[3], bloqueado=registro[4],fecha=registro[5])
                    return usuarios
                else:
                    return None
        except Exception as e:
            log.error(f"Error no se puedo acceder a la informacion del usuario:\n{e} ")

    @classmethod
    def Consultar_intentos_fallidos(cls, user: Usuario):
        try:
            with CursorSqlite3() as Cursor:
                Cursor.execute(cls.CONSULTAR_INTENTOS_FALLIDOS_BLOQUEO, (user.username,))
                registro = Cursor.fetchone()
                if registro is None:
                    return None
                usuarios = Usuario(id_usuario=registro[0],intentos_fallidos=registro[1],bloqueado=registro[2],fecha=registro[3])
                return usuarios
        except Exception as e:
            log.error(f"Error no se puedo acceder a la informacion de numero de intentos del usuario:\n{e} ")

    @classmethod
    def Actualizar_intentos_bloqueo(cls, user: Usuario):
        try:
            with CursorSqlite3() as Cursor:
                if user.bloqueado!=1:
                    Cursor.execute(cls.ACTUALIZAR_INTENTOS_FALLIDOS_BLOQUEO, (user.intentos_fallidos, user.bloqueado,user.id_usuario))
                else:
                    user.fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    Cursor.execute(cls.ACTUALIZAR_INTENTOS_FALLIDOS_BLOQUEO_FECHA,(user.intentos_fallidos, user.bloqueado,user.fecha,user.id_usuario))
                return Cursor.rowcount
        except Exception as e:
            log.error(f"Error al actualizar intentos fallidos y bloqueo de inicio de sesion:\n{e}")

    @classmethod
    def Actualizar_ultima_sesion(cls, user: Usuario):
        try:
            with CursorSqlite3() as Cursor:
                user.fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                Cursor.execute(cls.ACTUALIZAR_ULTIMA_SESION,
                               (user.fecha, user.id_usuario))
                return Cursor.rowcount
        except Exception as e:
            log.error(f"Error al actualizar la última sesión:\n{e}")
    @classmethod
    def Obtener_tiempo_minutos(cls):
        try:
            fecha_actual = datetime.datetime.now()
            fecha_usuario = datetime.datetime.strptime(user.fecha, "%Y-%m-%d %H:%M:%S")
            tiempo = fecha_actual - fecha_usuario
            minutos = tiempo.total_seconds() / 60
            return minutos
        except Exception as e:
            log.error(f"Error al obtener la diferencia de tiempo:\n{e}")
    @classmethod
    def inicio_sesion_exitosa(cls,user:Usuario):
        try:
            user.intentos_fallidos = 0
            user.bloqueado = 0
            cls.Actualizar_ultima_sesion(user)
            cls.Actualizar_intentos_bloqueo(user)
            cls.Insertar_registro_intento(user,texto=user.ACCIONES[0])
        except Exception as e:
            log.error(f"Error al iniciar sesion:\n{e}")


    @classmethod
    def inicio_sesion(cls,user:Usuario):
        usuario=cls.Acceso_app(user)
        if usuario:
            if usuario.bloqueado:
                minutos=cls.Obtener_tiempo_minutos()
                if minutos <15:
                    messagebox.showerror(
                        "Error de inicio de sesión",
                        "Por motivos de seguridad, su usuario ha sido bloqueado temporalmente "
                        f"durante {15-minutos:.0f} minutos. Espere e intente nuevamente o póngase en contacto "
                        "con el administrador de la aplicación.")
                    cls.Insertar_registro_intento(usuario,texto=usuario.ACCIONES[1])
                    return False
                else:
                    cls.inicio_sesion_exitosa(usuario)
                    return usuario

            cls.inicio_sesion_exitosa(usuario)
            return usuario
        else:
            usuario=cls.Consultar_intentos_fallidos(user)
            if usuario is not None:
                if usuario.bloqueado:
                    minutos = cls.Obtener_tiempo_minutos()
                    if minutos < 15:
                        messagebox.showerror(
                            "Error de inicio de sesión",
                            "Por motivos de seguridad, su usuario ha sido bloqueado temporalmente "
                            f"durante {15-minutos:.0f} minutos. Espere e intente nuevamente o póngase en contacto "
                            "con el administrador de la aplicación.")
                        cls.Insertar_registro_intento(usuario,texto=usuario.ACCIONES[1])
                        return False
                    else:

                        cls.inicio_sesion_exitosa(usuario)
                        return usuario
                else:
                    usuario.intentos_fallidos += 1
                    usuario.bloqueado = 1 if usuario.intentos_fallidos > 5 else 0
                    cls.Actualizar_intentos_bloqueo(usuario)
                    messagebox.showerror(
                        "Error Inicio sesion",
                        "Error de autenticación. Intente nuevamente."
                    )
                    cls.Insertar_registro_intento(usuario,texto=usuario.ACCIONES[1])
                    return False
            else:
                messagebox.showerror("Error Inicio sesion",f"Error de autenticación. No se encontro en el sistema al usuario:\n{user.username} ")
                return False


if __name__=="__main__":
    user=Usuario(id_usuario=2, username="felipe14@gmail.com", password="12345", rol="Administrador", intentos_fallidos=0, bloqueado=0)
    DAOMedicalOmni3D.Insertar_usuario(user)


