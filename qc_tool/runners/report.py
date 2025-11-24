from ..core.io import load_json
from ..export.text_report import generar_informe_texto
from ..config.settings import ensure_dirs

def main(record_path: str):
    ensure_dirs()
    rec = load_json(record_path)
    form = rec.get("form", {})
    generar_informe_texto(form)
    print("Informe TXT solicitado (si tu función lo genera, quedó en la ruta configurada)." )

if __name__ == "__main__":  # ejecución directa
    import sys
    if len(sys.argv) != 2:
        print("Uso: python -m qc_tool.runners.report <record.json>")
        raise SystemExit(2)
    main(sys.argv[1])
