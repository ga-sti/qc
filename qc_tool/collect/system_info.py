
import sys
from typing import Dict, Any
from ..config.settings import BASE_DIR

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# We will reuse your existing implementation to avoid behavior changes.
from sistema import obtener_info_detallada as _obtener_info_detallada
from sistema import detectar_so_activado as _detectar_so_activado
from sistema import detectar_motherboard as _detectar_motherboard

BASIC_KEYS = [
    "CPU",
    "RAM Total (GB)",
    "RAM Slots usados",
    "Tipo de RAM",
    "Disco Total (GB)",
    "GPU(s)",
]

def get_basics() -> Dict[str, Any]:
    """Devuelve un dict con los campos básicos de hardware/OS, sin cambiar tu lógica actual.
    Implementación: llama a tu 'obtener_info_detallada()' y extrae las claves básicas.
    """
    full = _obtener_info_detallada()
    basics: Dict[str, Any] = {k: full[k] for k in BASIC_KEYS if k in full}
    # S.OPERATIVO y MOTHER pueden no estar en 'basics' si el código cambia; los completamos:
    if "S.OPERATIVO" in full:
        basics["S.OPERATIVO"] = full["S.OPERATIVO"]
    else:
        so, act = _detectar_so_activado()
        basics["S.OPERATIVO"] = {"version": so, "activated": act}
    basics["MOTHER"] = full.get("MOTHER") or _detectar_motherboard()
    return basics
