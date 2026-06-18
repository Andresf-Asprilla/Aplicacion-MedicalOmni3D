import logging as log
import os
from platformdirs import PlatformDirs
dirs = PlatformDirs(appname="MedicalOmni3D", appauthor=False)
ruta_logs = dirs.user_log_dir
os.makedirs(ruta_logs, exist_ok=True)
log.basicConfig(level=log.INFO,format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] %(message)s',handlers=[log.FileHandler(os.path.join(ruta_logs, "MedicalOmni3d.log"),encoding="utf-8")])