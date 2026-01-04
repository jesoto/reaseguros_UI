import streamlit as st
from models.services import UserService
from recaptcha import recaptcha
from recaptcha.validate_recaptcha import validate_recaptcha_token, interpret_recaptcha_response
from constants import PUBLIC_SITE_KEY, API_KEY, GCP_PROJECT_ID, LOGO_URL, APP_NAME
import logging
import requests
import time
#logging.basicConfig(level=logging.DEBUG)

def login():
    _, col, _ = st.columns([1, 2, 1])

    if "captcha_valid" not in st.session_state:
        st.session_state["captcha_valid"] = False
        
    with col:
        logo_col, title_col = st.columns([1, 4.5])
        with logo_col:
            st.image(f"src/{LOGO_URL}", width=80)  # Asegurar que la imagen se cargue
        with title_col:
            st.markdown(f"<h1 style='margin: 0; text-align: left;'>{APP_NAME}</h1>", unsafe_allow_html=True)
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        button_col, captcha_col = st.columns([1, 2])  # Ajusta el ancho de las columnas según sea necesario

        with button_col:
            if st.button("Iniciar sesión"):
                try:
                    if not username or not password:
                        st.error("Por favor, ingresa tu usuario y contraseña.")
                        st.session_state["captcha_valid"] = False
                        return

                    user_service = UserService()
                    res = user_service.login_user(username, password)
                    
                    if res:  # Si el login es exitoso
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = username
                        st.session_state["app_role"] = res["user"]["is_admin"] 
                        st.rerun()
                        
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 400:
                        st.error("Usuario o contraseña incorrectos. Por favor, inténtalo nuevamente.")
                    else:
                        st.error(f"Error al iniciar sesión: {str(e)}")
                        
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {str(e)}")

        with captcha_col:
            if not st.session_state["captcha_valid"]:
                RECAPTCHA_ACTION = "login"
                token_captcha = recaptcha(PUBLIC_SITE_KEY, action=RECAPTCHA_ACTION)
                if token_captcha:
                    try:
                        response = validate_recaptcha_token(token_captcha, RECAPTCHA_ACTION, PUBLIC_SITE_KEY, API_KEY, GCP_PROJECT_ID)
                        if response:
                            is_human, score, reasons = interpret_recaptcha_response(response)
                            if is_human:
                                st.session_state["captcha_valid"] = True
                            else:
                                st.error(f"Verificación fallida. Puntuación: {score:.2f}")
                                if reasons:
                                    st.warning(", ".join(reasons))
                        else:
                            st.error("CAPTCHA inválido. Intente nuevamente.")
                    except Exception as e:
                        st.error(f"Error en la validación: {str(e)}")

# def logout():
#     keys_to_clear = ["app_access", "otp_verified", "otp_sent", 
#                     "start_time", "user_email", "app_role"]
    
#     for key in keys_to_clear:
#         if key in st.session_state:
#             del st.session_state[key]
    
#     st.session_state.clear()
#     with st.spinner("Cerrando sesión..."):
#         time.sleep(1)  

#     st.rerun()


def logout():
    """Cierra sesión completamente y redirige al login"""
    
    for key in list(st.session_state.keys()):
        if not key.startswith('_'):  
            del st.session_state[key]
    
    st.cache_data.clear()
    st.cache_resource.clear()
    
    with st.spinner("Cerrando sesión de manera segura..."):
        time.sleep(1.5)
        st.rerun()

    # 4. Bloqueo adicional de UI mientras se procesa
    st.stop()

