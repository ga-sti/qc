# qc_tool/config/settings.py
from pathlib import Path
import os, sys

def _code_base() -> Path:
    # Carpeta donde viven los archivos del programa (plantillas, assets…)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller (EXE onefile): recursos extraídos en _MEIPASS
        return Path(sys._MEIPASS)
    # Ejecución normal desde fuentes
    return Path(__file__).resolve().parents[2]

def _data_base() -> Path:
    # Carpeta donde ESCRIBIMOS cosas (json, excel, logs)
    # Por defecto C:\QC_Auto, o bien variable de entorno QC_DATA_DIR
    return Path(os.environ.get("QC_DATA_DIR", r"C:\QC_Auto"))

CODE_BASE     = _code_base()                  # lectura (recursos)
DATA_BASE     = _data_base()                  # escritura (salidas)
ORACULOS_DIR  = DATA_BASE / "oraculos"
ASSETS_DIR    = DATA_BASE / "assets"          # si algún día quisieras copiar algo aquí
TEMPLATES_DIR = CODE_BASE                     # QCPC.xlsx y QCLAPTOP.xlsx viven con el código

def ensure_dirs():
    DATA_BASE.mkdir(parents=True, exist_ok=True)
    ORACULOS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# --- ALIASES de retrocompatibilidad ---
BASE_DIR = CODE_BASE        # 👈 para módulos que sigan importando BASE_DIR
PROJECT_ROOT = CODE_BASE    # 👈 por si algún archivo viejo usa PROJECT_ROOT
