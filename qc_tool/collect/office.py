
import sys
from typing import Optional
from ..config.settings import BASE_DIR

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Reuse current implementation without changing logic
from sistema import detectar_office_preciso as _detectar_office_preciso

def detectar_office_preciso() -> Optional[str]:
    """Wrapper: devuelve la versión/edición detectada de Office (misma lógica actual)."""
    return _detectar_office_preciso()
