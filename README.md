# 🖥️ QC Automatizado - Herramienta de Auditoría Técnica (v1.5)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)
![Windows](https://img.shields.io/badge/OS-Windows-blue)

**QC Automatizado** es una solución integral de software diseñada para el departamento de Soporte Técnico. Su objetivo es estandarizar, acelerar y documentar el proceso de Control de Calidad (QC) de equipos informáticos (PCs y Laptops) mediante la recolección automática de datos del sistema y la ejecución de pruebas de hardware interactivas.

---

## ✨ Características Principales

### 🔍 Extracción Automática de Sistema (WMI & PowerShell)
- **Hardware:** Detección precisa de Procesador (CPU), Gráficos (GPU), Motherboard, RAM (Capacidad, Slots, Tipo DDR) y Almacenamiento.
- **Identidad:** Captura del Hostname, Número de Serie de la BIOS, Dominio/Entra ID y versión exacta del Sistema Operativo (incluyendo estado de activación).
- **Auditoría de Software:** Verificación nativa en el Registro de Windows y rutas de instalación para software corporativo crítico (Google Chrome, 7-Zip, TeamViewer, FortiClient VPN, Java, Endpoint Agent, Adobe Acrobat Reader/DC y Antivirus).

### 🛠️ Pruebas Interactivas de Hardware
El sistema guía al técnico a través de pruebas manuales y semi-automáticas:
- **Puertos USB:** Escaneo dinámico de inserción/extracción física usando `pnputil` y `wmic`.
- **Conectividad:** Detección de enlace de red (RJ45), conexión de monitores externos (HDMI/DisplayPort) y redes Wi-Fi.
- **Periféricos:** Test integral de teclado (mapeo completo) y mouse (clics y scroll).
- **Webcam:** Verificación de video en tiempo real utilizando OpenCV.
- **Energía:** Detección del estado de alimentación AC y batería.

### ⚡ Interfaz Gráfica Fluida (Multithreading)
Construida con **PyQt6**, la aplicación utiliza un diseño moderno con carga diferida (*Lazy Loading*). Las pruebas que requieren consultas pesadas al sistema operativo (PowerShell) se ejecutan en hilos secundarios (`QThread`), garantizando que la interfaz se mantenga 100% responsiva y sin "congelamientos".

### 📊 Generación de Reportes Profesionales (Openpyxl)
Toda la auditoría se compila y exporta de manera automática:
- **Mapeo Inteligente en Excel:** Inserción de datos en coordenadas exactas dentro de plantillas predefinidas (`QCPC.xlsx` y `QCLAPTOP.xlsx`), incluyendo la validación de etiquetas (Sello de Garantía, Licencia COA, AT Service con código asociado).
- **Log de Texto:** Generación de un reporte `.txt` detallado de respaldo.
- **Guardado Resiliente:** Sistema *anti-crash* que detecta si el archivo de destino está bloqueado o abierto por el usuario, generando automáticamente copias de seguridad con *timestamp*.

---

## 📂 Estructura del Proyecto

```text
qc/
│
├── start_qc.py             # Punto de entrada de la aplicación
├── src/
│   ├── interfaz.py         # Lógica de la GUI, ventanas y navegación
│   ├── pruebas.py          # Clases QDialog, QThread y testeo de hardware (Webcam, USB, Red)
│   ├── extractor.py        # Motor de recolección de datos (WMI, Registro, psutil)
│   ├── exportador.py       # Motor de escritura de Excel y gestión de guardado
│   ├── modelos.py          # Dataclasses para estructurar la información
│   ├── configuracion.py    # Rutas base y configuraciones del entorno
│   └── botones.py          # Componentes visuales personalizados de PyQt6
│
└── assets/                 # Iconos, fondos y plantillas de Excel (.xlsx)
