import os, sys
from typing import Dict, Any
from ..config.settings import BASE_DIR, ORACULOS_DIR
from ..core.io import save_json, timestamp

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from interfaz import obtener_datos_formulario  # usa tu UI actual

def get_form() -> Dict[str, Any]:
    return obtener_datos_formulario()

def run_and_save() -> str:
    form = get_form()
    out = ORACULOS_DIR / f"form_{timestamp()}.json"
    save_json(form, str(out))
    return str(out)
