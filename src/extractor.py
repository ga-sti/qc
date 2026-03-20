# src/extractor.py
import winreg
import os
import psutil
import platform
import wmi
import socket
import time
import concurrent.futures
import pythoncom
from typing import List, Optional, Tuple, Dict

try:
    import win32api
except ImportError:
    win32api = None

from src.modelos import DatosSistema

# ==========================================
# CACHÉS WMI Y CONEXIONES (Hilo Principal)
# ==========================================
_wmi = None
_wmi_sc2 = None

def _get_wmi():
    """Instancia compartida para evitar lentitud por reconexión."""
    global _wmi
    if _wmi is None:
        try:
            _wmi = wmi.WMI(moniker=r"winmgmts:\\.\root\cimv2")
        except:
            _wmi = wmi.WMI()
    return _wmi

def obtener_wmi_sc2():
    """Conexión específica para Antivirus (SecurityCenter2)."""
    global _wmi_sc2
    if _wmi_sc2 is None:
        try:
            _wmi_sc2 = wmi.WMI(namespace=r"root\SecurityCenter2")
        except:
            pass
    return _wmi_sc2

# ==========================================
# FUNCIONES PARA HILOS (MULTITHREADING)
# ==========================================
# REGLA: Cada hilo nuevo en Python que use WMI NECESITA inicializar COM.

def _get_cpu_info():
    """Ejecutado en hilo secundario."""
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI(moniker=r"winmgmts:\\.\root\cimv2")
        nombre = c.Win32_Processor()[0].Name.strip()
    except:
        nombre = "Desconocido"
    finally:
        pythoncom.CoUninitialize()
    return nombre

def _get_so_activacion_info():
    """Ejecutado en hilo secundario."""
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI(moniker=r"winmgmts:\\.\root\cimv2")
        os_info = c.Win32_OperatingSystem()[0]
        so_edition = getattr(os_info, "Caption", f"Windows {platform.release()}")
        
        query = "SELECT LicenseStatus FROM SoftwareLicensingProduct WHERE PartialProductKey IS NOT NULL AND Name LIKE '%Windows%'"
        activado = any(getattr(p, "LicenseStatus", 0) == 1 for p in c.query(query))
    except:
        so_edition, activado = f"Windows {platform.release()}", False
    finally:
        pythoncom.CoUninitialize()
    return so_edition, activado

# ==========================================
# LÓGICAS DE DETECCIÓN TÉCNICA
# ==========================================

def obtener_numero_serie() -> str:
    try:
        c = _get_wmi()
        bios = c.Win32_BIOS()[0]
        sn = bios.SerialNumber
        if sn and sn.strip().lower() not in ["", "none", "0000000", "default string", "to be filled by o.e.m."]:
            return sn.strip().upper()
    except: pass
    return "No detectado"

def detectar_office_preciso() -> Optional[str]:
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration") as k:
            v, _ = winreg.QueryValueEx(k, "VersionToReport")
            if v: return f"Microsoft 365 ({v})"
    except: pass

    office_keys = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Office") as office_key:
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(office_key, i)
                    if subkey.count('.') == 1: office_keys.append(subkey)
                    i += 1
                except OSError: break
    except: return "No detectado"

    if not office_keys: return "No detectado"
    highest = sorted(office_keys, reverse=True)[0]

    if highest == "16.0":
        rutas = [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE"
        ]
        file_version = None
        for ruta in rutas:
            if os.path.exists(ruta) and win32api:
                try:
                    info = win32api.GetFileVersionInfo(ruta, "\\")
                    ms = info['FileVersionMS']
                    file_version = f"{ms >> 16}.{ms & 0xFFFF}"
                    break
                except: continue

        if file_version:
            if file_version.startswith("16.0.4"): return "Office 2016"
            if file_version.startswith("16.0.10"): return "Office 2019"
            if file_version.startswith("16.0.14"): return "Office 2021"
        return "Office 2016/19/21"
    
    version_map = {"15.0": "Office 2013", "14.0": "Office 2010", "12.0": "Office 2007"}
    return version_map.get(highest, "No detectado")

def detectar_antivirus() -> List[str]:
    c_sc2 = obtener_wmi_sc2()
    if not c_sc2: return ["Windows Defender"]
    try:
        avs = [av.displayName for av in c_sc2.AntivirusProduct()]
        return avs if avs else ["Windows Defender"]
    except:
        return ["Windows Defender"]

def verificar_dominio() -> str:
    try:
        c = _get_wmi()
        cs = c.Win32_ComputerSystem()[0]
        if cs.PartOfDomain and cs.Domain.lower() != "workgroup":
            return f"Dominio: {cs.Domain}"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Enrollments", 0, winreg.KEY_READ) as key:
                if winreg.QueryInfoKey(key)[0] > 0: return "Entra ID (Azure AD)"
        except: pass
    except: pass
    return "Local / Grupo de Trabajo"


# ==========================================
# ORQUESTADOR PRINCIPAL (HILOS + RECURSOS)
# ==========================================

def recolectar_sistema() -> DatosSistema:
    # 🟢 INICIALIZAR MONITOR DE RECURSOS DEL PROPIO PROGRAMA
    proceso_actual = psutil.Process(os.getpid())
    ram_inicial_mb = proceso_actual.memory_info().rss / (1024 * 1024)
    proceso_actual.cpu_percent(interval=None) # Llamada en blanco para iniciar lectura

    print("\n" + "="*50)
    print("--- [MICRO-PROFILER] INICIANDO EXTRACCIÓN ALTO RENDIMIENTO ---")
    print(f"  > RAM Inicial del programa: {ram_inicial_mb:.2f} MB")
    print("="*50)

    t_inicio_total = time.perf_counter()

    # 🟢 LANZAR TAREAS PESADAS A HILOS DE FONDO
    # Manda la CPU (1.1s) y el S.O (1.4s) a resolverse en otros núcleos del procesador
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    future_cpu = executor.submit(_get_cpu_info)
    future_so = executor.submit(_get_so_activacion_info)

    # 🟢 MIENTRAS TANTO, EL HILO PRINCIPAL HACE LAS TAREAS RÁPIDAS
    t0 = time.perf_counter()
    c = _get_wmi()
    print(f"  > WMI Conexión principal: {time.perf_counter() - t0:.4f}s")

    t0 = time.perf_counter()
    ram_total, ram_slots, ram_tipo = 0, 0, "DDRx"
    try:
        for m in c.Win32_PhysicalMemory():
            ram_total += int(m.Capacity)
            ram_slots += 1
            t = int(getattr(m, "SMBIOSMemoryType", 0))
            if t == 24: ram_tipo = "DDR3"
            elif t == 26: ram_tipo = "DDR4"
            elif t == 34: ram_tipo = "DDR5"
    except: pass
    ram_gb = round(ram_total / (1024**3))
    print(f"  > Lectura RAM:            {time.perf_counter() - t0:.4f}s")

    t0 = time.perf_counter()
    disco_total = 0
    for p in psutil.disk_partitions():
        if 'fixed' in p.opts:
            try: disco_total += psutil.disk_usage(p.mountpoint).total
            except: continue
    disco_gb = round(disco_total / (1024**3))
    print(f"  > Lectura Discos:         {time.perf_counter() - t0:.4f}s")

    t0 = time.perf_counter()
    try: gpu_info = [g.Name for g in c.Win32_VideoController()]
    except: gpu_info = ["No detectada"]
    print(f"  > Lectura GPU:            {time.perf_counter() - t0:.4f}s")

    t0 = time.perf_counter()
    rutas_apps = {
        "chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
        "7zip": [r"C:\Program Files\7-Zip\7z.exe"],
        "teamviewer": [r"C:\Program Files\TeamViewer\TeamViewer.exe", r"C:\Program Files (x86)\TeamViewer\TeamViewer.exe"],
        "forti_vpn": [r"C:\Program Files\Fortinet\FortiClient\FortiClient.exe"],
        "java": [r"C:\Program Files\Java", r"C:\Program Files (x86)\Java"],
        "endpoint": [
            r"C:\Program Files (x86)\ManageEngine\UEMS_Agent\dcconfig.exe", 
            r"C:\Program Files\ManageEngine\UEMS_Agent\dcconfig.exe", 
            r"C:\Program Files (x86)\DesktopCentral_Agent\bin\dcutil.exe"
        ],
        # 🟢 RUTA CORREGIDA PARA ADOBE ACROBAT (DC y Reader)
        "adobe_reader": [
            r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
            r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe", 
            r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
        ]
    }
    sw_detectado = {app: any(os.path.exists(r) for r in paths) for app, paths in rutas_apps.items()}
    print(f"  > Detección Software:     {time.perf_counter() - t0:.4f}s")

    t0 = time.perf_counter()
    try: mother = c.Win32_BaseBoard()[0].Product.strip()
    except: mother = "Desconocida"
    print(f"  > Motherboard:            {time.perf_counter() - t0:.4f}s")
    
    t0 = time.perf_counter()
    dominio = verificar_dominio()
    print(f"  > Dominio:                {time.perf_counter() - t0:.4f}s")
    
    t0 = time.perf_counter()
    antivirus = detectar_antivirus()
    print(f"  > Antivirus:              {time.perf_counter() - t0:.4f}s")
    
    t0 = time.perf_counter()
    office_ver = detectar_office_preciso()
    print(f"  > Office:                 {time.perf_counter() - t0:.4f}s")
    
    t0 = time.perf_counter()
    n_serie = obtener_numero_serie()
    print(f"  > Número de Serie:        {time.perf_counter() - t0:.4f}s")

    # 🟢 RECOLECTAR RESULTADOS DE LOS HILOS PESADOS
    # Si las consultas terminaron antes que nuestras lecturas rápidas, esto es instantáneo.
    # Si no, esperamos los milisegundos que falten.
    t0 = time.perf_counter()
    cpu_nombre = future_cpu.result()
    so_nombre, so_activado = future_so.result()
    executor.shutdown()
    print(f"  > Sincronización Hilos:   {time.perf_counter() - t0:.4f}s")

    # 🟢 RESULTADOS FINALES DE RECURSOS
    ram_final_mb = proceso_actual.memory_info().rss / (1024 * 1024)
    cpu_usada = proceso_actual.cpu_percent(interval=None)
    
    print("="*50)
    print(f"--- [MICRO-PROFILER] FIN EXTRACCIÓN ---")
    print(f"  > Tiempo Total:           {time.perf_counter() - t_inicio_total:.4f}s")
    print(f"  > Pico de CPU usado:      {cpu_usada:.1f}%")
    print(f"  > RAM Final del programa: {ram_final_mb:.2f} MB (+{ram_final_mb - ram_inicial_mb:.2f} MB)")
    print("="*50 + "\n")

    return DatosSistema(
        hostname=socket.gethostname(),
        mother=mother,
        cpu=cpu_nombre,
        gpu=gpu_info,
        ram_gb=ram_gb,
        ram_slots=ram_slots,
        ram_tipo=ram_tipo,
        disco_total_gb=disco_gb,
        s_operativo=so_nombre,
        activado=so_activado,
        dominio=dominio,
        antivirus=antivirus,
        software=sw_detectado,
        office={"version": office_ver},
        numero_serie=n_serie
    )