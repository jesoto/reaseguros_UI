# Componente reCAPTCHA para Streamlit

Componente personalizado que integra Google reCAPTCHA v3 en aplicaciones Streamlit.

## Instalación

```bash
git clone https://github.com/Rimac-Seguros/streamlit-recaptcha.git

cd streamlit-recaptcha

pip install -e .
```

## Uso

```python
import streamlit as st
from streamlit_recaptcha import recaptcha

# Configurar clave de sitio
site_key = "TU_CLAVE_DE_SITIO_RECAPTCHA"

# Obtener token de reCAPTCHA
token = recaptcha(site_key, action="login")

# Verificar si se obtuvo el token
if token:
    st.success("Verificación completada")
    # Continuar con el flujo de la aplicación
```

## Validación en backend

```python
from streamlit_recaptcha.validate_recaptcha import validate_recaptcha_token, interpret_recaptcha_response

api_key = "TU_CLAVE_API"

# Validar token
response = validate_recaptcha_token(token, "login", site_key, api_key)
is_human, score, reasons = interpret_recaptcha_response(response)

if is_human:
    # Usuario verificado, continuar el proceso
    pass
else:
    # Posible bot, rechazar la solicitud
    pass
```