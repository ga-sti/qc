# start_qc.py  (en la raíz del proyecto)
import sys

# Importamos el entrypoint como módulo de paquete.
from qc_tool.runners.pipeline import main

if __name__ == "__main__":
    sys.exit(main() or 0)
