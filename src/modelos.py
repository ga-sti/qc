# src/modelos.py
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class DatosFormulario:
    """Datos capturados desde la interfaz gráfica del técnico."""
    equipo: Optional[str] = None
    realizado_por: Optional[str] = None
    cliente: Optional[str] = None
    usb: Optional[int] = None
    hw: Optional[Dict[str, Optional[bool]]] = None
    sw: Optional[Dict[str, Optional[bool]]] = None
    sellos: Optional[Dict[str, Optional[bool]]] = None
    codigo_at: Optional[str] = None

@dataclass
class DatosSistema:
    """Datos extraídos automáticamente del hardware y software del equipo."""
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
    numero_serie: Optional[str] = None  # 🟢 NUEVO CAMPO AGREGADO