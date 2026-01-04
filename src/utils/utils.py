import streamlit as st
import uuid
from datetime import datetime
import pytz
import logging
import re
from pathlib import Path
from google.cloud import storage
import re
from urllib.parse import quote
from typing import Optional 

logging.basicConfig(level=logging.INFO)

peru_timezone = pytz.timezone('America/Lima')

def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 ** 2:
        size_in_kb = size_in_bytes / 1024
        return f"{size_in_kb:.2f} KB"
    elif size_in_bytes < 1024 ** 3:
        size_in_mb = size_in_bytes / (1024 ** 2)
        return f"{size_in_mb:.2f} MB"
    else:
        size_in_gb = size_in_bytes / (1024 ** 3)
        return f"{size_in_gb:.2f} GB"

def format_date(date_str):
    # Parse the input date string
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Set the timezone to UTC and convert to the target timezone
    dt_utc = dt.replace(tzinfo=pytz.utc)
    dt_local = dt_utc.astimezone(peru_timezone)
    
    # Format the date in the desired format
    formatted_date = dt_local.strftime("%Y-%m-%d (%H:%M)")
    return formatted_date

def extract_number(string):
    match = re.search(r'\d+', string)
    return int(match.group()) if match else None

def get_current_time():
    return datetime.now(peru_timezone).strftime("%Y-%m-%d %H:%M:%S")

def new_session_id():
    st.session_state.session_id = str(uuid.uuid4())
    
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_uris_set" not in st.session_state:
        st.session_state.uploaded_uris_set = []
    if "uploaded_xlsx" not in st.session_state:
        st.session_state.uploaded_xlsx = None
    if "xlsx_df" not in st.session_state:
        st.session_state.xlsx_df = None
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0
    if "file_uploader_xlsx_key" not in st.session_state:
        st.session_state.file_uploader_xlsx_key = 1000
    if "processing_xlsx" not in st.session_state:
        st.session_state.processing_xlsx = False
    if 'confirmed_upload' not in st.session_state:
        st.session_state.confirmed_upload = False 
    # if "session_id" not in st.session_state:
    #     new_session_id()
    if "feedback_rendered" not in st.session_state:
        st.session_state.feedback_rendered = False
    if "clear_container" not in st.session_state:
        st.session_state.clear_container = False
    if "feedback_collected" not in st.session_state:
        st.session_state.feedback_collected = False
    
    if "show_extra_metadata_modal" not in st.session_state:
        st.session_state.show_extra_metadata_modal = False
    if "extra_messages" not in st.session_state:
        st.session_state.extra_messages = []

def truncate_text(text, max_len=30):
    return text if len(text) <= max_len else text[:max_len] + "..."


def load_css(file_name):
    file_path = Path(__file__).resolve().parent.parent / file_name
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def upload_document_to_gcs(bucket_name, source_file, destination_blob_name, content_type):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(source_file, content_type=content_type)
    uri = f"gs://{bucket_name}/{destination_blob_name}"
    return uri

def clean_markdown_text(text):
    if not text:
        return ""
    text = text.replace('\\n', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def parse_gs_uri(gs_uri: str):
    """
    Devuelve (bucket, blob) a partir de 'gs://bucket/path/al/objeto.ext'
    """
    m = re.match(r'^gs://([^/]+)/(.+)$', gs_uri)
    if not m:
        return None, None
    return m.group(1), m.group(2)

def build_gcs_console_url(gs_uri: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    Crea una URL a la Consola GCP (pestaña de detalles del objeto).
    """
    bucket, blob = parse_gs_uri(gs_uri)
    if not bucket or not blob:
        return None
    blob_enc = quote(blob, safe='')  # encode path completo
    base = f"https://console.cloud.google.com/storage/browser/_details/{bucket}/{blob_enc}"
    if project_id:
        base += f"?project={project_id}"
    return base

def filename_from_gs_uri(gs_uri: str) -> str:
    return gs_uri.rstrip('/').split('/')[-1]