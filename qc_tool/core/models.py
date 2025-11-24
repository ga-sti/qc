from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class FormData:
    # Mantener claves y estructura actuales; el adapter de UI devuelve un dict.
    equipo: Optional[str] = None        # 'PC' o 'Laptop' (o valores abreviados como 'PC'/'LAP')
    realizado_por: Optional[str] = None
    cliente: Optional[str] = None
    usb: Optional[int] = None
    hw: Optional[Dict[str, Optional[bool]]] = None      # dvd/cargador/hdmi/rj45/teclado/webcam
    sw: Optional[Dict[str, Optional[bool]]] = None      # drivers_ok, wifi_ok
    sellos: Optional[Dict[str, Optional[bool]]] = None  # at_service, micro, garantia, coa

@dataclass
class SystemData:
    hostname: Optional[str] = None
    mother: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[List[str]] = None
    ram_gb: Optional[int] = None
    ram_slots: Optional[int] = None
    ram_tipo: Optional[str] = None
    disco_total_gb: Optional[int] = None
    s_operativo: Optional[str] = None
    activado: Optional[bool] = None
    dominio: Optional[str] = None
    antivirus: Optional[List[str]] = None
    software: Optional[Dict[str, bool]] = None
    office: Optional[Dict[str, Optional[str]]] = None

@dataclass
class QCRecord:
    fecha_hora: str
    form: Dict
    system: Dict
