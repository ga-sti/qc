import openpyxl
import unicodedata
from pathlib import Path

def _norm(s: str) -> str:
    if s is None: return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if ord(c) < 128)
    return s.strip().upper()

# Equivalente a tu LABELS_PC original (Columna B)
ETIQUETAS_B = {
    "fecha_hora":       ["FECHA/HORA"],
    "realizado_por":    ["REALIZADO POR", "QC REALIZADO POR", "QC REALIZADO POR:"],
    "cliente":          ["CLIENTE"],
    "mother":           ["MOTHER"],
    "cpu":              ["CPU"],
    "gpu":              ["GPU", "GPU(S)"],
    "memoria_ram":      ["MEMORIA RAM"],
    "disco_duro_1":     ["DISCO DURO 1"],
    "disco_duro_2":     ["DISCO DURO 2"],
    "cd_dvd_rw":        ["CD / DVD RW", "LECTORA DVD"],
    "usb":              ["USB", "PUERTOS USB"],
    "cable_de_poder":   ["CABLE DE PODER", "CARGADOR"],
    "teclado":          ["TECLADO (TESTEAR)"],
    "webcam":           ["WEBCAM"],
    "hdmi":             ["HDMI"],
    "rj45":             ["RJ45"],
    "s_operativo":      ["S.OPERATIVO /ACTIVACION", "S.OPERATIVO"],
    "drivers":          ["DRIVERS"],
    "office":           ["OFFICE"],
    "antivirus":        ["ANTIVIRUS"],
    "endpoint_central": ["ENDPOINT CENTRAL"],
    "adobe_reader":     ["ADOBE READER"],
    "teamviewer":       ["TEAMVIEWER"],
    "7zip":             ["7ZIP"],
    "forticlient":      ["FORTI CLIENT VPN", "FORTICLIENT"],
    "chrome":           ["CHROME"],
    "java":             ["JAVA"],
    "dominio":          ["DOMINIO"],
    "wifi":             ["WIFI"],
    "numero_serie":     ["NUMERO DE SERIE", "NÚMERO DE SERIE"] # 🟢 AGREGADO
}

# Equivalente a tu SELLOS_PC original (Columna G)
ETIQUETAS_G = {
    "sello_at_service": ["AT SERVICE"],
    "micro_intel_amd":  ["MICRO INTEL/AMD"],
    "sello_garantia":   ["SELLO GARANTIA", "SELLO GARANTÍA"],
    "coa_windows":      ["COA WINDOWS"],
    "qc_rehecho":       ["QC REHECHO"]
}

def _escanear_columna(ws, columna: str, etiquetas_buscadas: list) -> int | None:
    normalizadas = [_norm(l) for l in etiquetas_buscadas]
    for fila in range(1, 100):
        val = ws[f"{columna}{fila}"].value
        if val and _norm(val) in normalizadas:
            return fila
    return None

def obtener_mapa_dinamico(ruta_plantilla: Path) -> dict:
    """Escanea el Excel y devuelve: {'clave': ('Columna', Fila)}"""
    wb = openpyxl.load_workbook(ruta_plantilla, data_only=True)
    ws = wb.active
    mapa = {}

    for clave, labels in ETIQUETAS_B.items():
        fila = _escanear_columna(ws, "B", labels)
        if fila: mapa[clave] = ("C", fila) # Ancla la escritura en la Col C

    for clave, labels in ETIQUETAS_G.items():
        fila = _escanear_columna(ws, "G", labels)
        if fila: mapa[clave] = ("G", fila) # Ancla en G (para cruces en H/I)

    return mapa