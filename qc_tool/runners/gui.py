from ..ui.form import run_and_save
from ..config.settings import ensure_dirs

def main():
    ensure_dirs()
    path = run_and_save()
    print("Formulario guardado en:", path)

if __name__ == "__main__":
    main()
