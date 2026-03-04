# qc_tool/runners/pipeline.py

from __future__ import annotations

import threading
from ..config.settings import ensure_dirs, ORACULOS_DIR
from ..ui.form import run_and_save as run_gui
from ..collect.aggregate import run_and_save as run_collect
from ..core.io import save_json, load_json, timestamp
from ..runners.excel import main as run_excel
from ..runners.report import main as run_report
from ..ui.progress import ProgressUI


def run_pipeline() -> None:
    ensure_dirs()

    # 1) UI principal
    form_path = run_gui()


    # Cancelación: si el usuario cerró la UI, no seguimos ni abrimos la progress bar
    if not form_path:
        print('[i] Operación cancelada por el usuario. No se ejecuta el pipeline.')
        return

    # 2) Ventana de progreso (Tk en hilo principal)
    prog = ProgressUI(title="Procesando QC", subtitle="Aguarde…")

    result: dict[str, object] = {"record_path": None, "error": None}

    def worker() -> None:
        # <<<--- COM init (requerido para WMI en threads)
        import pythoncom
        pythoncom.CoInitialize()
        try:
            # 3) Recolección (WMI)
            prog.set_message("Recolectando información del sistema…")
            system_path = run_collect()

            # 4) Merge y record
            prog.set_message("Combinando datos…")
            form = load_json(form_path)
            system = load_json(system_path)
            rec = {"fecha_hora": timestamp(), "form": form, "system": system}
            record_path = ORACULOS_DIR / f"record_{rec['fecha_hora']}.json"
            save_json(rec, str(record_path))
            result["record_path"] = str(record_path)

            # 5) Excel
            prog.set_message("Generando planilla Excel…")
            run_excel(str(record_path))

            # 6) TXT
            prog.set_message("Creando informe de texto…")
            run_report(str(record_path))

            # 7) Fin
            prog.done("¡OK!")
        except Exception as e:
            result["error"] = e
            prog.done("Ocurrió un error")
        finally:
            # <<<--- COM uninit
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

    # Lanzar trabajo pesado
    threading.Thread(target=worker, daemon=True).start()

    # Mantener la ventanita viva
    prog.mainloop()

    if result["error"]:
        raise result["error"]
    if result["record_path"]:
        print("\nPipeline OK. Record:", result["record_path"])


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
