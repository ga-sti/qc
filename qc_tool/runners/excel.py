from ..core.io import load_json
from ..export.excel_writer import guardar_en_excel
from ..config.settings import ensure_dirs

def main(record_path: str):
    ensure_dirs()
    rec = load_json(record_path)
    form = rec.get("form", {})
    system = rec.get("system", {})
    tipo = str(form.get("Tipo de equipo", "")).upper()
    es_pc = ("PC" in tipo) and ("LAP" not in tipo)
    xlsx = guardar_en_excel(datos_form=form, datos_sist=system, es_pc=es_pc)
    print("Excel generado:", xlsx)

if __name__ == "__main__":  # ejecución directa
    import sys
    if len(sys.argv) != 2:
        print("Uso: python -m qc_tool.runners.excel <record.json>")
        raise SystemExit(2)
    main(sys.argv[1])
