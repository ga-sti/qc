# src/pipeline.py
import threading
import pythoncom
import time

# ==========================================
# PROFILER: Medición de Tiempos de Importación
# ==========================================
print("\n" + "="*50)
print(">>> [PROFILER] INICIANDO ARRANQUE DE LA APP")
print("="*50)

t_import_start = time.perf_counter()

# Importaciones absolutas (Aquí suele estar el cuello de botella al abrir)
from src.interfaz import lanzar_interfaz, ProgressUI
t_interfaz_loaded = time.perf_counter()
print(f"[PROFILER] Modulo 'interfaz' cargado en: {t_interfaz_loaded - t_import_start:.3f}s")

from src.extractor import recolectar_sistema
t_extractor_loaded = time.perf_counter()
print(f"[PROFILER] Modulo 'extractor' cargado en: {t_extractor_loaded - t_interfaz_loaded:.3f}s")

from src.exportador import exportar_excel
t_exportador_loaded = time.perf_counter()
print(f"[PROFILER] Modulo 'exportador' cargado en: {t_exportador_loaded - t_extractor_loaded:.3f}s")

from src.modelos import DatosFormulario, DatosSistema
print(f"[PROFILER] IMPORTACIONES TOTALES: {time.perf_counter() - t_import_start:.3f}s\n")

def ejecutar_pipeline():
    """Punto de entrada: Lanza la UI de pestañas."""
    print(">>> [PROFILER] Lanzando Motor Gráfico (PyQt6)...")
    t_ui_start = time.perf_counter()
    
    # Lanzamos la interfaz. El bloqueo ocurre aquí hasta que se cierre la app.
    lanzar_interfaz(callback_generar=iniciar_proceso_tecnico)

def iniciar_proceso_tecnico(datos_form: DatosFormulario):
    """
    Controlador de la etapa técnica post-formulario.
    """
    print("\n" + "="*50)
    print(">>> [PROFILER] INICIANDO EXTRACCIÓN Y GUARDADO")
    print("="*50)
    
    t_proceso_start = time.perf_counter()
    progreso = ProgressUI(title="Motor de Extracción AT", subtitle="Inicializando hilos...")

    def worker():
        # REGLA DE ORO: Inicializar COM en el hilo donde se usará WMI
        pythoncom.CoInitialize()
        t_com_init = time.perf_counter()
        print(f"[PROFILER] Hilo y COM inicializados en: {t_com_init - t_proceso_start:.3f}s")
        
        try:
            # ETAPA 1: Extracción de Hardware y Software
            progreso.set_message("Analizando Procesador, RAM y Software...")
            print(">>> [PROFILER] Ejecutando 'recolectar_sistema()'...")
            
            t_ext_start = time.perf_counter()
            datos_sist = recolectar_sistema()
            t_ext_end = time.perf_counter()
            print(f"[PROFILER] Extracción completada en: {t_ext_end - t_ext_start:.3f}s")
            
            # ETAPA 2: Generación del Reporte (Excel + Log)
            progreso.set_message("Generando reporte Excel y Log técnico...")
            print(">>> [PROFILER] Ejecutando 'exportar_excel()'...")
            
            t_exp_start = time.perf_counter()
            ruta_final = exportar_excel(datos_form, datos_sist)
            t_exp_end = time.perf_counter()
            print(f"[PROFILER] Escritura en disco completada en: {t_exp_end - t_exp_start:.3f}s")
            
            # ETAPA 3: Cierre y resumen
            t_total = time.perf_counter() - t_proceso_start
            print("="*50)
            print(f">>> [PROFILER] TIEMPO TOTAL DEL PROCESO TÉCNICO: {t_total:.3f}s")
            print("="*50)
            
            # Mandamos cartel a través de la señal
            texto_exito = f"Reporte generado con éxito en:\n{ruta_final}\n\nTiempo de procesamiento: {t_total:.1f} seg."
            progreso.finalizar_proceso("Proceso finalizado correctamente", "QC Automatizado", texto_exito)

        except Exception as e:
            print(f"!!! [PIPELINE ERROR] {str(e)}")
            import traceback; traceback.print_exc()
            
            texto_error = f"Error en la extracción:\n{str(e)}"
            progreso.finalizar_proceso("Fallo en la extracción", "Error del Sistema", texto_error)
            
        finally:
            pythoncom.CoUninitialize()

    # Iniciar hilo de fondo y mostrar ventana de carga
    threading.Thread(target=worker, daemon=True).start()
    progreso.exec()