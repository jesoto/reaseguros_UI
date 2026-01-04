# principal.py
import streamlit as st
import logging
from models.services import ReasegurosService
from annotated_text import annotated_text
from streamlit_extras.add_vertical_space import add_vertical_space
from constants import LOGO_URL, APP_NAME, BUCKET_NAME
from utils.utils import *
from pathlib import Path
import base64
import uuid

# Configuración de Logging
logger = logging.getLogger(__name__)

# Instancia de servicios
ReasegurosCore = ReasegurosService()

def upload_poliza_callback():
    """Registro histórico de la póliza en el bucket principal"""
    uploaded_poliza = st.session_state.get(st.session_state.poliza_key)    
    case_id = st.session_state.get("case_id")
    if uploaded_poliza:        
        try:
            uri = upload_document_to_gcs(
                bucket_name=BUCKET_NAME, 
                source_file=uploaded_poliza.getvalue(),
                destination_blob_name=f"Reaseguros/{case_id}/poliza/{uploaded_poliza.name}",
                content_type=uploaded_poliza.type
            )
            st.session_state.uploaded_poliza = {'name': uploaded_poliza.name, 'file_url': uri}
            st.success(f"✅ Póliza guardada históricamente")
        except Exception as e:
            st.error(f"❌ Error al subir a GCS: {str(e)}")

def upload_contratos_callback():
    """Registro histórico de los contratos en el bucket principal"""
    case_id = st.session_state.get("case_id")
    uploaded_contratos = st.session_state.get(st.session_state.contratos_key)
    if uploaded_contratos:
        contratos_docs = []        
        for contrato in uploaded_contratos:
            try:
                uri = upload_document_to_gcs(
                    bucket_name=BUCKET_NAME,
                    source_file=contrato.getvalue(),
                    destination_blob_name=f"Reaseguros/{case_id}/contratos/{contrato.name}",
                    content_type=contrato.type
                )
                contratos_docs.append({'name': contrato.name, 'file_url': uri})
            except Exception as e:
                st.error(f"❌ Error en {contrato.name}: {str(e)}")
        st.session_state.uploaded_contratos = contratos_docs

def go_to_principal_page():
    # Inicialización de estados core
    if 'uploaded_poliza' not in st.session_state: st.session_state.uploaded_poliza = None
    if 'uploaded_contratos' not in st.session_state: st.session_state.uploaded_contratos = []
    if "case_id" not in st.session_state: st.session_state["case_id"] = f"{get_current_time()}_{str(uuid.uuid4())[:8]}"
    if "analysis_completed" not in st.session_state: st.session_state.analysis_completed = False
    if "uploader_reset" not in st.session_state: st.session_state.uploader_reset = 0
    if "poliza_key" not in st.session_state: st.session_state.poliza_key = f"p_{st.session_state.uploader_reset}"
    if "contratos_key" not in st.session_state: st.session_state.contratos_key = f"c_{st.session_state.uploader_reset}"

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(APP_NAME)
        st.write(f"**Usuario:** {st.session_state.user_email}")
        add_vertical_space(1)
        
        st.file_uploader("Subir Póliza", type=["pdf"], key=st.session_state.poliza_key, on_change=upload_poliza_callback)
        st.file_uploader("Subir Contratos", type=["pdf"], key=st.session_state.contratos_key, accept_multiple_files=True, on_change=upload_contratos_callback)
        
        if st.button("New Analysis"):
            st.session_state.uploader_reset += 1
            st.rerun()

    # --- MAIN CONTENT ---
    st.header("📊 Generador de Resumen Gerencial")
    
    files_uploaded = st.session_state.uploaded_poliza and st.session_state.uploaded_contratos
    
    if st.button("🚀 Generar Análisis LangGraph", type="primary", disabled=not files_uploaded):
        with st.status("🧠 Procesando con LangGraph...", expanded=True) as status:
            try:
                # 1. Obtenemos archivos desde los uploaders de sesión
                pol_file = st.session_state.get(st.session_state.poliza_key)
                con_files = st.session_state.get(st.session_state.contratos_key)
                
                # 2. Llamada al Servicio Integrado
                result = ReasegurosCore.process_workflow(pol_file, con_files)
                
                if not result['success']:
                    raise Exception(result['error'])

                pdf_content = result['content']
                pdf_name = f"reporte_{st.session_state.case_id}.pdf"

                # 3. Guardar en el nuevo bucket 'reaseguros-bot'
                st.write("💾 Guardando resultado en `reaseguros-bot`...")
                pdf_uri = upload_document_to_gcs(
                    bucket_name="reaseguros-bot",
                    source_file=pdf_content,
                    destination_blob_name=f"outputs/{st.session_state.case_id}/{pdf_name}",
                    content_type="application/pdf"
                )

                st.session_state.pdf_generated = {
                    'content': pdf_content,
                    'name': pdf_name,
                    'uri': pdf_uri
                }
                st.session_state.analysis_completed = True
                status.update(label="✅ Éxito!", state="complete")

            except Exception as e:
                st.error(f"Hubo un problema: {str(e)}")
                status.update(label="❌ Falló", state="error")

    # --- RESULTADOS ---
    if st.session_state.analysis_completed:
        st.divider()
        res = st.session_state.pdf_generated
        st.success("¡Análisis listo!")
        st.download_button("💾 Descargar PDF", data=res['content'], file_name=res['name'], mime="application/pdf")
        st.info(f"Reporte almacenado en: {res['uri']}")