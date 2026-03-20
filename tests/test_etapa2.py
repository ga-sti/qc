import unittest
import sys
from src.extractor import recolectar_sistema

class TestEtapa2(unittest.TestCase):
    def test_extraccion_paso_a_paso(self):
        print("\n[1/4] Iniciando recolección de sistema...")
        sys.stdout.flush() # Fuerza a Windows a mostrar el texto ya
        
        datos = recolectar_sistema()
        
        print(f"[2/4] Hardware detectado: {datos.cpu}")
        print(f"[3/4] Office detectado: {datos.office['version']}")
        print(f"[4/4] Software detectado: {list(datos.software.keys())}")
        
        self.assertIsNotNone(datos.hostname)
        print("\n¡Prueba completada con éxito!")

if __name__ == "__main__":
    unittest.main()