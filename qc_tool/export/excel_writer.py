import sys, importlib, time
from typing import Dict, Any, Optional
from ..config.settings import BASE_DIR

# asegurar imports desde la raíz del proyecto
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

orig = importlib.import_module('guardar_excel')

# intentar importar el mapping nuevo (si existe) para monkeypatch
try:
    from ..core import mapping as newmap
except Exception:
    newmap = None

if newmap is not None:
    for name in ['MAP_PC','MAP_LAPTOP','NORMALIZED_MAP','FIELD_MAP','NORMALIZED_LABELS','normalize_label']:
        try:
            if hasattr(newmap, name) and hasattr(orig, name):
                setattr(orig, name, getattr(newmap, name))
        except Exception:
            pass

def guardar_en_excel(
    datos_form: Dict[str, Any],
    datos_sist: Dict[str, Any],
    es_pc: bool,
    output_path: Optional[str] = None
) -> str:
    t0 = time.time()
    x = orig.guardar_en_excel(datos_form=datos_form, datos_sist=datos_sist, es_pc=es_pc, output_path=output_path)
    t1 = time.time()
    print(f"[excel] Tiempo generar Excel: {t1 - t0:.2f}s  (plantilla={'PC' if es_pc else 'LAP'})")
    return x