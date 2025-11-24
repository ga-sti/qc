
from typing import Dict, Any
from ..core.io import save_json, timestamp
from ..config.settings import ORACULOS_DIR

# Submódulos separados (wrappers a tu código actual)
from .system_info import get_basics
from .office import detectar_office_preciso
from .software import detectar_software, detectar_antivirus, verificar_dominio

def collect_system_info() -> Dict[str, Any]:
    """Arma el MISMO dict que antes devolvía sistema.obtener_info_detallada(),
    pero orquestando módulos separados.
    """
    info: Dict[str, Any] = {}

    # 1) Básicos (CPU/RAM/Disco/GPU + SO + MOTHER)
    info.update(get_basics())

    # 2) Office
    info["Office"] = detectar_office_preciso()

    # 3) Software instalado (Chrome, 7-Zip, TeamViewer, Adobe Reader, FortiClient, Java, Endpoint)
    info.update(detectar_software())

    # 4) Antivirus (lista)
    info["Antivirus"] = detectar_antivirus()

    # 5) Dominio (string o None)
    info["Unido a dominio"] = verificar_dominio()

    return info

def run_and_save() -> str:
    data = collect_system_info()
    out = ORACULOS_DIR / f"system_{timestamp()}.json"
    save_json(data, str(out))
    return str(out)
