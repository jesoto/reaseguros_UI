# app.py
import streamlit as st # type:ignore
import time
import os
from utils.utils import load_css
from pages.principal import go_to_principal_page
from constants import LOGO_URL, LOGO_RIMAC, CSS_PATH, APP_NAME, APP_VERSION
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno si existe un .env (opcional para local)
load_dotenv()

def initialize_session_state():
    """Inicializa las variables necesarias para el flujo LangGraph y Auth"""
    session_defaults = {
        "app_access": True,
        "otp_verified": True,
        "user_email": "usuario_reaseguros@rimac.com.pe",
        "app_role": True,
        "uploader_reset": 0 # Necesario para limpiar los uploaders después del éxito
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 1. Configuración de página (SIEMPRE PRIMERO)
file_path_icon = Path(__file__).resolve().parent / LOGO_URL
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon=str(file_path_icon) if file_path_icon.exists() else "🛡️",
    layout="wide"
)

# 2. Inicializar estado
initialize_session_state()

# 3. UI: Logo y Header
st.logo(LOGO_RIMAC, icon_image=LOGO_RIMAC, size="large")

col1, col2 = st.columns([7, 2])
load_css(CSS_PATH)

with col1:
    st.markdown(f'<div class="styled-header">{APP_NAME}</div>', unsafe_allow_html=True)

with col2:
    # Intenta buscar el logo en src si el primer path falló
    logo_path = Path(__file__).resolve().parent.parent / 'src' / LOGO_URL
    if logo_path.exists():
        st.image(str(logo_path), width=150)

# 4. Lanzar página principal
go_to_principal_page()