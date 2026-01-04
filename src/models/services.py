import requests
import logging
from models.apiclient import APIClient
from constants import API_URL, API_CORE, REQUIRED_ROLE

logger = logging.getLogger(__name__)

class ReasegurosService:
    """
    Servicio para la arquitectura LangGraph.
    Consolida todo el flujo en el endpoint: api/documents/process-workflow
    """
    def __init__(self):
        # API_CORE es la URL base de tu Cloud Run
        self.client = APIClient(API_CORE)
        
    def process_workflow(self, poliza_file, contrato_files):
        """
        Ejecuta el flujo completo de Reaseguros:
        1. Desestructuración.
        2. Comparación múltiple.
        3. Generación de Reporte PDF.
        """
        endpoint = "api/documents/process-workflow"
        url = f"{self.client.base_url}/{endpoint}"
        
        # 1. Obtenemos headers base (Token Auth)
        raw_headers = self.client._get_headers()
        
        # 2. LIMPIEZA DE HEADERS: 
        # Es vital eliminar 'Content-Type' para que la librería requests 
        # genere automáticamente el header multipart/form-data con el boundary correcto.
        headers = {k: v for k, v in raw_headers.items() if k.lower() != 'content-type'}
        
        # 3. Preparación de archivos para Multipart
        # El formato debe ser: (nombre_campo, (nombre_archivo, bytes, mime_type))
        files = [
            ('poliza', (poliza_file.name, poliza_file.getvalue(), poliza_file.type))
        ]
        
        for cf in contrato_files:
            files.append(('contratos', (cf.name, cf.getvalue(), cf.type)))
            
        try:
            logger.info(f"🚀 Iniciando petición a LangGraph API: {url}")
            
            # El timeout de 300s (5 min) es crucial para procesos de IA largos
            response = requests.post(
                url, 
                files=files, 
                headers=headers, 
                timeout=300
            )
            
            if response.status_code == 200:
                logger.info("✅ Respuesta exitosa recibida del servidor.")
                return {
                    'success': True,
                    'content': response.content,  # Los bytes del PDF
                    'filename': 'reporte_reaseguros_consolidado.pdf',
                    'size_bytes': len(response.content)
                }
            else:
                # Intentamos parsear el error detallado del backend
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                
                logger.error(f"❌ Error en API ({response.status_code}): {error_data}")
                return {
                    'success': False,
                    'error': error_data,
                    'status_code': response.status_code
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "La petición excedió el tiempo límite de 5 minutos. El documento podría ser muy extenso."
            }
        except Exception as e:
            logger.exception("Error crítico de comunicación")
            return {
                'success': False,
                'error': f"Error de comunicación con el servicio: {str(e)}"
            }

class CoreService:
    """
    Servicio para utilidades generales del APP (histórico, etc.)
    """
    def __init__(self):
        self.client = APIClient(API_URL)

    # Aquí puedes mantener otros métodos auxiliares si los necesitas
    pass