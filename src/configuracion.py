import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Any

def obtener_ruta_recurso(ruta_relativa: str) -> Path:
    """
    Retorna la ruta absoluta para recursos (plantillas, logos).
    Se comunica perfectamente con PyInstaller (_MEIPASS) o ejecución en desarrollo.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        # Sube de src/ -> raíz del proyecto
        base_path = Path(__file__).resolve().parents[1]
    return base_path / ruta_relativa

def obtener_ruta_datos() -> Path:
    """Determina dónde se guardarán los resultados. Por defecto C:\\QC_Auto"""
    return Path(os.environ.get("QC_DATA_DIR", r"C:\QC_Auto"))

# --- CONSTANTES GLOBALES EXPORTADAS ---
RUTA_DATOS = obtener_ruta_datos()
DIR_REPORTES = RUTA_DATOS / "reportes"
DIR_PLANTILLAS = obtener_ruta_recurso("plantillas")
DIR_ASSETS = obtener_ruta_recurso("assets")

def inicializar_directorios() -> None:
    """Garantiza que existan las carpetas necesarias antes de guardar."""
    RUTA_DATOS.mkdir(parents=True, exist_ok=True)
    DIR_REPORTES.mkdir(parents=True, exist_ok=True)

# --- UTILIDADES DE ENTRADA/SALIDA (Ex io.py) ---
def generar_marca_tiempo() -> str:
    """Devuelve timestamp con el formato YYYYMMDD_HHMMSS."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def guardar_json(datos: Any, ruta_archivo: str | Path) -> str:
    """Guarda un diccionario o lista en formato JSON de forma segura."""
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    return str(ruta)

def leer_json(ruta_archivo: str | Path) -> Any:
    """Carga un JSON y lo devuelve como objeto de Python."""
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return json.load(f)