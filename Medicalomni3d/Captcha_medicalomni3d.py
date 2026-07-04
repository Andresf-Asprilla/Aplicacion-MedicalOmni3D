import os
from captcha.image import ImageCaptcha
from  Medicalomni3d.Configuracion_Apcivmapcas import Configuracionnnunetv2
from matplotlib import font_manager
from tkinter import messagebox
import random
import string
import  matplotlib.pyplot as plt
from  matplotlib.image import imread

class CaptchaMedicalOmni3D:
    LONGITUD=6
    BASE_DIR_CAPTCHA=os.path.join(Configuracionnnunetv2.BASE_DIR,"captcha.png")
    FUENTES = [font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans")),font_manager.findfont(font_manager.FontProperties(family="DejaVu Serif")),font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans Mono"))]
    @classmethod
    def Generar_texto(cls):
        caracteres = string.ascii_lowercase + string.digits
        return ''.join(random.choice(caracteres) for _ in range(cls.LONGITUD))
    @classmethod
    def Generar_captcha(cls):
        captcha=ImageCaptcha(width=150,height=110,fonts=cls.FUENTES,font_sizes=(40,70,100))
        texto=cls.Generar_texto()
        print(texto)
        captcha.write(texto,cls.BASE_DIR_CAPTCHA)
        return texto,cls.BASE_DIR_CAPTCHA

if __name__=="__main__":
    texto,ruta=CaptchaMedicalOmni3D.Generar_captcha()
    imagen=imread(ruta)
    plt.imshow(imagen)
    plt.show()
