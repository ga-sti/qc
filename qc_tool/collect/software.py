
import sys
from typing import Dict, Any, List, Optional
from ..config.settings import BASE_DIR

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sistema import detectar_software as _detectar_software
from sistema import detectar_antivirus as _detectar_antivirus
from sistema import verificar_dominio as _verificar_dominio
from sistema import detectar_endpoint_central as _detectar_endpoint_central

def detectar_software() -> Dict[str, Any]:
    """Wrapper a tu función actual (Chrome, 7zip, TeamViewer, Adobe, Forti, Java, Endpoint, etc.)."""
    data = _detectar_software()
    # Algunas instalaciones (Endpoint) pueden tener un helper dedicado; nos aseguramos de incluirlo.
    if "Endpoint Central" not in data:
        try:
            data["Endpoint Central"] = bool(_detectar_endpoint_central())
        except Exception:
            # mantener compatibilidad con tu implementación original si falla
            pass
    return data

def detectar_antivirus() -> List[str]:
    return _detectar_antivirus()

def verificar_dominio() -> Optional[str]:
    return _verificar_dominio()
