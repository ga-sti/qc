import os, sys
from typing import Dict, Any
from ..config.settings import BASE_DIR

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sistema import mostrar_info_terminal  # tu función actual

def generar_informe_texto(form_dict: Dict[str, Any]) -> None:
    try:
        mostrar_info_terminal(form_dict)
    except Exception as e:
        # No bloqueamos el pipeline si falla el TXT
        print("[WARN] mostrar_info_terminal falló:", e)
