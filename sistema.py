import winreg
import os
import psutil
import platform
import wmi
import socket

from config import INFO_TXT

# =========================
# Detectar Office preciso
# =========================
def detectar_office_preciso():
    try:
        # Verificar si es Microsoft 365 ClickToRun
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration") as k:
            v, _ = winreg.QueryValueEx(k, "VersionToReport")
            if v:
                return f"Microsoft 365 ({v})"
    except Exception:
        pass

    office_keys = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Office") as office_key:
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(office_key, i)
                    if subkey.count('.') == 1:
                        office_keys.append(subkey)
                    i += 1
                except OSError:
                    break
    except:
        return "Office no encontrado"

    if not office_keys:
        return "Office no encontrado"

    highest = sorted(office_keys, reverse=True)[0]
    version_map = {
        "15.0": "Office 2013",
        "14.0": "Office 2010",
        "12.0": "Office 2007"
    }

    if highest == "16.0":
        rutas = [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE"
        ]
        file_version = None
        for ruta in rutas:
            if os.path.exists(ruta):
                try:
                    import win32api
                    info = win32api.GetFileVersionInfo(ruta, "\\")
                    ms = info['FileVersionMS']
                    ls = info['FileVersionLS']
                    major = ms >> 16
                    minor = ms & 0xFFFF
                    build = ls >> 16
                    rev = ls & 0xFFFF
                    file_version = f"{major}.{minor}.{build}.{rev}"
                    break
                except:
                    continue

        if file_version:
            if file_version.startswith("16.0.4") or file_version.startswith("16.0.43"):
                office_version_detected = "Office 2016"
            elif file_version.startswith("16.0.10"):
                office_version_detected = "Office 2019"
            elif file_version.startswith("16.0.14"):
                office_version_detected = "Office 2021"
            elif file_version.startswith("16.0.1") or file_version.startswith("16.0.2"):
                office_version_detected = "Microsoft 365"
            else:
                office_version_detected = f"Office versión desconocida ({file_version})"
        else:
            office_version_detected = "Office 16.0 instalado (ejecutable no encontrado)"
    else:
        office_version_detected = version_map.get(highest, f"Versión desconocida ({highest})")

    return office_version_detected


# =========================
# Detectar motherboard
# =========================
def detectar_motherboard():
    try:
        c = wmi.WMI()
        boards = c.Win32_BaseBoard()
        if boards:
            return boards[0].Product.strip()
    except Exception:
        pass
    return None


# =========================
# Detectar sistema operativo
# =========================
def detectar_so_activado():
    try:
        c = wmi.WMI(namespace=r"root\CIMV2")
        os_info = c.Win32_OperatingSystem()[0]
        so_edition = (os_info.Caption or "").strip()
        if so_edition.upper().startswith("MICROSOFT "):
            so_edition = so_edition[10:]

        GUID_WINDOWS = "55c92734-d682-4d71-983e-d6ec3f16059f"
        prods = c.SoftwareLicensingProduct(ApplicationID=GUID_WINDOWS)

        activated = False
        if prods:
            def is_windows(p):
                name = ((getattr(p, "Name", "") or "") + " " +
                        (getattr(p, "Description", "") or "")).upper()
                return "WINDOWS" in name

            def score(p):
                s = 0
                if getattr(p, "LicenseStatus", 0) == 1:
                    s += 10
                if is_windows(p):
                    s += 3
                if getattr(p, "PartialProductKey", None):
                    s += 2
                if getattr(p, "ProductKeyID", None):
                    s += 1
                return s

            best = max(prods, key=score)
            activated = (getattr(best, "LicenseStatus", 0) == 1)

            if not activated:
                activated = any(
                    getattr(p, "LicenseStatus", 0) == 1 and is_windows(p)
                    for p in prods
                )

        return so_edition, activated

    except Exception:
        try:
            return f"{platform.system()} {platform.release()}", False
        except Exception:
            return "Windows", False


# =========================
# Detectar software instalado
# =========================
def detectar_software():
    buscados = {
        "Adobe Reader": False,
        "Endpoint Central": detectar_endpoint_central(),
        "TeamViewer": False,
        "7-Zip": False,
        "FortiClient": False,
        "Google Chrome": False,
        "Java": False,
    }

    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for root, path in reg_paths:
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            for app in buscados:
                                if app.lower() in display_name.lower():
                                    buscados[app] = True
                    except:
                        continue
        except:
            continue

    return buscados


# =========================
# Detectar antivirus
# =========================
def detectar_antivirus():
    try:
        c = wmi.WMI(namespace="root\\SecurityCenter2")
        productos = c.AntiVirusProduct()
        return [p.displayName for p in productos] if productos else ["No detectado"]
    except:
        return ["Error al detectar"]


# =========================
# Verificar si está en dominio
# =========================
def verificar_dominio():
    try:
        c = wmi.WMI()
        sys_info = c.Win32_ComputerSystem()[0]
        if sys_info.PartOfDomain:
            return sys_info.Domain
        else:
            return None
    except:
        return None


# =========================
# Detectar Endpoint Central
# =========================
def detectar_endpoint_central():
    rutas_posibles = [
        r"C:\Program Files (x86)\ManageEngine\UEMS_Agent"
    ]

    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            return True
    return False


# =========================
# Obtener información detallada
# =========================
def obtener_info_detallada():
    c = wmi.WMI()
    cpu_info = c.Win32_Processor()[0]
    cpu_nombre = cpu_info.Name.strip()

    ram_modules = c.Win32_PhysicalMemory()
    ram_total = sum([int(r.Capacity) for r in ram_modules])
    ram_slots = len(ram_modules)
    TIPOS_RAM = {
        20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM",
        24: "DDR3", 25: "DDR4", 26: "DDR5"
    }
    ram_tipo = TIPOS_RAM.get(ram_modules[0].MemoryType, "Desconocido") if ram_modules else "Desconocido"

    discos = psutil.disk_partitions()
    disco_total = 0
    for d in discos:
        if "cdrom" in d.opts or d.fstype == "":
            continue
        try:
            uso = psutil.disk_usage(d.mountpoint)
            disco_total += uso.total
        except:
            continue

    gpus = c.Win32_VideoController()
    gpu_info = [gpu.Name for gpu in gpus] if gpus else ["No detectada"]

    info = {
        "CPU": cpu_nombre,
        "RAM Total (GB)": round(ram_total / (1024**3), 2),
        "RAM Slots usados": ram_slots,
        "Tipo de RAM": ram_tipo,
        "Disco Total (GB)": round(disco_total / (1024**3), 2),
        "GPU(s)": gpu_info
    }

    info["Office"] = detectar_office_preciso()
    info.update(detectar_software())
    info["Antivirus"] = detectar_antivirus()
    info["Unido a dominio"] = verificar_dominio()
    so, so_activado = detectar_so_activado()
    info["S.OPERATIVO"] = {"version": so, "activated": so_activado}
    info["MOTHER"] = detectar_motherboard()

    print(f"🔍 Motherboard rápida: {info['MOTHER']!r}")
    return info


# =========================
# Mostrar información en terminal
# =========================
def mostrar_info_terminal(formulario):
    info = obtener_info_detallada()
    info.update(formulario)

    texto = ""
    for k, v in info.items():
        if isinstance(v, list):
            texto += f"{k}: {', '.join(v)}\n"
        else:
            texto += f"{k}: {v}\n"

    print("\n--- Información del sistema ---")
    print(texto)

    with open(INFO_TXT, "w", encoding="utf-8") as f:
        f.write(texto)
