import streamlit as st
import time
import base64
from models.services import OTPService
from constants import OTP_TOKEN_EXPIRE_TIME, OTP_TOKEN_LEN

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_otp():
    load_css("src/assets/styles.css")
    otp_service = OTPService()
    columns = st.columns([1,1,1])
    with columns[1]:
        st.markdown(
            """
            <div class="styled-title">
                Verifica tu Correo Electronico 
            </div>
            """,
            unsafe_allow_html=True,
        )
        image_path = "src/assets/mail3.png"
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode()
        image_url = f"data:image/png;base64,{image_base64}"
        st.markdown(f"""
                    <div style="display: flex; justify-content: center;">
                        <img src="{image_url}" alt="emoji" style="width:80px; vertical-align: middle;">
                    </div>
                    """, unsafe_allow_html=True)
    
        st.markdown(
            f"""
            <div class="styled-text">
                Hemos enviado un codigo a tu e-mail. Por favor ingresalo.
            </div>
            """,
            unsafe_allow_html=True,
        )
        email = st.session_state.get("user_email", "")
        timer_placeholder = st.empty()
        
        otp_code = st.text_input(
            label="Código OTP", 
            max_chars=int(OTP_TOKEN_LEN), 
            key="otp_code",
            placeholder="Introduce el código de 6 dígitos",
            label_visibility="collapsed"
        )
        
        _, center, _ = st.columns([1,1,1])
        with center:
            verify_button = st.button(label='Validar codigo', type="primary")
        
        if verify_button:
            try:
                response = otp_service.validate_otp(email, otp_code)
                if response:
                    st.session_state["otp_valid"] = True
                    st.session_state["otp_verified"] = True
                    st.session_state["authenticated"] = True
                    # Asignar el rol basado en app_role (True para Admin, False para User)
                    if st.session_state.app_role:
                        st.session_state.role = "Admin"
                    else:
                        st.session_state.role = "User"
                    st.success("¡Código válido! Redirigiendo a la app...")
                    st.rerun()
                else:
                    st.error("La validación del código falló. Por favor intenta nuevamente.")
            except Exception as e:
                error_message = str(e)
                if "400" in error_message:
                    st.error("Código OTP inválido. Por favor, verifica e inténtalo de nuevo.")
                elif "500" in error_message:
                    st.error("Error interno del servidor. Inténtalo más tarde.")
                else:
                    st.error(f"Ocurrió un error inesperado: {error_message}")

        
        while True:
            elapsed_time = time.time() - st.session_state['start_time']
            remaining_time = float(OTP_TOKEN_EXPIRE_TIME) - elapsed_time  # 5 minutes countdown

            if remaining_time > 0:
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                timer_placeholder.markdown(
                    f"""
                    <div class="styled-subtitle-2">
                        Tiempo restante: {minutes}:{seconds:02d}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                time.sleep(1)
            else:
                st.warning("Codigo expirado. Solicita uno nuevo.")
                st.session_state['otp_sent'] = False
                st.session_state['otp_expired']  = True
                break
                    
        if not st.session_state['otp_sent'] and st.session_state['otp_expired']:
            _, center_1, _ = st.columns([1,1,1])
            with center_1:
                if st.button(label='Reenviar codigo', type="secondary"):
                    otp_service.send_otp(email)
                    print("----> call getotp response..")
                    st.session_state['start_time'] = time.time()
                    st.session_state['otp_sent'] = True
                    st.rerun()

def send_otp(email: str):
    if not st.session_state.otp_sent:
        otp_service = OTPService()
        otp_service.send_otp(email)
        st.session_state.otp_sent = True
        st.session_state.start_time = time.time()
        st.success("Código OTP enviado a tu correo.")
        time.sleep(1)
        st.rerun()