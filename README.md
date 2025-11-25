# QC Automatizado

Herramienta interna para hacer **control de calidad (QC)** de PCs y Laptops en forma rápida y consistente.

El objetivo es:

- Recolectar automáticamente **info de hardware y software** del equipo.
- Completar una **planilla Excel de QC** basada en plantillas (`QCPC.xlsx` y `QCLAPTOP.xlsx`) respetando exactamente las coordenadas definidas.
- Guardar los resultados (Excel + JSON / reportes) en una ubicación centralizada (idealmente el pendrive desde donde se ejecuta).

Está pensada para usarse desde un **pendrive**, correr el QC en cada equipo y salir con todos los informes generados.

---

## 🧱 Arquitectura general

Estructura lógica del proyecto:

- `start_qc.py`  
  Script de entrada (launcher) que llama al pipeline completo.

- `guardar_excel.py`  
  Lógica principal de escritura en Excel:
  - Carga las plantillas `QCPC.xlsx` (PC) y `QCLAPTOP.xlsx` (Laptop).
  - Mapea campos internos → coordenadas específicas de celdas.
  - Escribe textos y cruces (`X`) en la planilla de QC.

- `QCPC.xlsx` / `QCLAPTOP.xlsx`  
  Plantillas de Excel con el diseño del checklist de QC para:
  - Equipos de escritorio (PC)
  - Laptops

- `qc_tool/`
  - `config/settings.py`  
    - Define `BASE_DIR`, rutas base y `ensure_dirs()` para crear directorios necesarios.  
  - `runners/pipeline.py`  
    - Orquesta todo el flujo de trabajo (pipeline).
  - `runners/excel.py`  
    - Llama a la exportación a Excel.
  - `runners/report.py`  
    - Opcional: genera reportes complementarios (txt, etc.).
  - `export/excel_writer.py`  
    - Hace de puente entre el pipeline
