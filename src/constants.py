import os
import yaml
from google.cloud import secretmanager
from dotenv import load_dotenv


# Cargar variables locales del .env como prioridad para desarrollo
load_dotenv()

gcp_secret = os.getenv("GCP_SECRET")
project_id = os.getenv("PROJECT_ID")

print(f"DEBUG: raw GCP_SECRET='{gcp_secret}', PROJECT_ID='{project_id}'")

if gcp_secret and not gcp_secret.startswith("projects/"):
    if project_id:
        print("DEBUG: constructing full path from short name and PROJECT_ID")
        gcp_secret = f"projects/{project_id}/secrets/{gcp_secret}/versions/latest"
    else:
        print("WARNING: GCP_SECRET looks like a short name but PROJECT_ID is missing!")

print(f"DEBUG: final GCP_SECRET='{gcp_secret}'")

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
REQUIRED_ROLE = app_credentials["REQUIRED_ROLE"]
API_CORE = app_credentials["API_CORE"]
BUCKET_NAME = app_credentials["BUCKET_NAME"]
GCP_PROJECT_ID = app_credentials["GCP_PROJECT_ID"]



