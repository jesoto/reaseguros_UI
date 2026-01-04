from google.cloud import secretmanager
import yaml
import os
from dotenv import load_dotenv

# Cargar variables locales del .env como prioridad para desarrollo
load_dotenv()

# Función auxiliar para obtener configuración (Prioridad: ENV > GCP Secret)
def get_config(key, secrets, default=None):
    return os.getenv(key) or secrets.get(key, default)

# Carga de Secretos desde GCP
gcp_secret = os.getenv("GCP_SECRET")
client = secretmanager.SecretManagerServiceClient()
response = client.access_secret_version(name=gcp_secret)
my_secret_value = response.payload.data.decode("UTF-8")
app_credentials = yaml.safe_load(my_secret_value)

# Configuración de Activos y App
LOGO_URL = "assets/logo.png"
LOGO_RIMAC = "src/assets/rimac-seguros.png"
CSS_PATH = "assets/styles.css"
APP_NAME = "Reaseguros Bot"
APP_VERSION = "V1.0.0"

# Variables Críticas (Priorizan .env si existe)
REQUIRED_ROLE = get_config("REQUIRED_ROLE", app_credentials, "reaseguros-bot")
API_CORE = get_config("API_CORE", app_credentials)
BUCKET_NAME = get_config("BUCKET_NAME", app_credentials, "reaseguros-bot")
GCP_PROJECT_ID = get_config("GCP_PROJECT_ID", app_credentials)

# API_URL se mantiene por compatibilidad si es necesario, 
# aunque API_CORE es la principal ahora
API_URL = get_config("API_URL", app_credentials)
API_KEY = get_config("API_KEY", app_credentials)
