import unittest
import os
import shutil
from pathlib import Path
from src.modelos import DatosFormulario, DatosSistema
from src.configuracion import (
    obtener_ruta_recurso, 
    guardar_json, 
    leer_json, 
    inicializar_directorios,
    DIR_REPORTES
)

class TestEtapa1(unittest.TestCase):
    
    def setUp(self):
        """Prepara un entorno temporal antes de cada test."""
        self.ruta_test_json = Path("test_temporal.json")

    def tearDown(self):
        """Limpia el entorno después de cada test."""
        if self.ruta_test_json.exists():
            self.ruta_test_json.unlink()
            
    def test_modelos_instanciacion(self):
        """Verifica que los modelos aceptan los datos correctamente."""
        form = DatosFormulario(equipo="Laptop", realizado_por="Gasti")
        sistema = DatosSistema(hostname="PC-AT-01", ram_gb=16)
        
        self.assertEqual(form.equipo, "Laptop")
        self.assertEqual(sistema.ram_gb, 16)
        self.assertIsNone(sistema.cpu) # Campo no asignado debe ser None

    def test_guardar_y_leer_json(self):
        """Verifica la comunicación de IO guardando y leyendo un dict real."""
        datos_prueba = {"hardware": {"cpu": "Intel", "ram": 16}, "activo": True}
        
        # Test Guardar
        ruta_guardada = guardar_json(datos_prueba, self.ruta_test_json)
        self.assertTrue(Path(ruta_guardada).exists())
        
        # Test Leer
        datos_leidos = leer_json(ruta_guardada)
        self.assertEqual(datos_prueba, datos_leidos)

    def test_rutas_recursos(self):
        """Verifica que el resolutor de rutas no devuelva strings vacíos."""
        ruta_plantillas = obtener_ruta_recurso("plantillas")
        self.assertTrue(isinstance(ruta_plantillas, Path))
        self.assertIn("plantillas", str(ruta_plantillas))

if __name__ == "__main__":
    unittest.main()