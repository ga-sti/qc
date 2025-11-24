from ..core.io import load_json, save_json, timestamp
from ..config.settings import ORACULOS_DIR, ensure_dirs

def merge(form_path: str, system_path: str) -> str:
    form = load_json(form_path)
    system = load_json(system_path)
    record = {"fecha_hora": timestamp(), "form": form, "system": system}
    out = ORACULOS_DIR / f"record_{record['fecha_hora']}.json"
    save_json(record, str(out))
    return str(out)

def main(form_path: str, system_path: str):
    ensure_dirs()
    out = merge(form_path, system_path)
    print("Record combinado en:", out)

if __name__ == "__main__":  # ejecución directa: ejemplo rápido
    import sys
    if len(sys.argv) != 3:
        print("Uso: python -m qc_tool.runners.merge <form.json> <system.json>")
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
