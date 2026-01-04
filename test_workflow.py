import os
import sys
from pathlib import Path
from io import BytesIO

# Añadir src al path para poder importar los módulos
src_path = str(Path(__file__).resolve().parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from models.services import ReasegurosService

class MockUploadedFile:
    """Clase sencilla para simular un objeto de archivo de Streamlit"""
    def __init__(self, name, content, type="application/pdf"):
        self.name = name
        self.content = content
        self.type = type
    
    def getvalue(self):
        return self.content

def run_test():
    print("🚀 Iniciando prueba técnica del Workflow de Reaseguros...")
    
    # 1. Instanciar el servicio
    service = ReasegurosService()
    
    # 2. Crear archivos PDF de prueba mínimos (o usar reales si existieran)
    # Aquí creamos un buffer de bytes para simular PDFs
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    
    poliza_mock = MockUploadedFile("poliza_test.pdf", dummy_pdf_content)
    contrato_mock = MockUploadedFile("contrato_test.pdf", dummy_pdf_content)
    
    print(f"📦 Archivos preparados: {poliza_mock.name} y {contrato_mock.name}")
    print("📡 Enviando petición a la API (Timeout: 300s)...")
    
    try:
        # 3. Ejecutar el workflow
        # El servicio espera un objeto con .name, .getvalue() y .type (como en el nuevo service.py)
        result = service.process_workflow(
            poliza_file=poliza_mock,
            contrato_files=[contrato_mock]
        )
        
        if result['success']:
            print("✅ ¡ÉXITO! El workflow respondió correctamente.")
            print(f"📄 Archivo generado: {result['filename']}")
            print(f"⚖️ Tamaño: {result['size_bytes'] / 1024:.2f} KB")
            
            # Guardar localmente para inspección visual
            output_path = "test_output_reporte.pdf"
            with open(output_path, "wb") as f:
                f.write(result['content'])
            print(f"💾 Reporte de prueba guardado en: {os.path.abspath(output_path)}")
            
        else:
            print("❌ ERROR en el Workflow:")
            print(f"Status Code: {result.get('status_code')}")
            print(f"Detalle: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 Error crítico durante la ejecución: {str(e)}")

if __name__ == "__main__":
    run_test()
