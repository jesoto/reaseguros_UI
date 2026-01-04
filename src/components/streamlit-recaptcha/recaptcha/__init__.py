import os
import streamlit as st
import streamlit.components.v1 as components

# En producción, cargamos el componente desde el directorio build
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_component_func = components.declare_component("recaptcha", path=build_dir)

def recaptcha(site_key, action=None, debug=False, key=None):
    """
    Integra reCAPTCHA en una aplicación de Streamlit.
    
    Este componente carga reCAPTCHA y devuelve un token que puede ser
    verificado en el backend para determinar si el usuario es legítimo.
    
    Parameters
    ----------
    site_key: str
        La clave del sitio reCAPTCHA obtenida de la consola de Google.
    
    action: str (opcional)
        La acción que se está protegiendo, como "login", "signup", etc.
        Este valor se utiliza para análisis en la consola de reCAPTCHA.
    
    debug: bool (opcional)
        Si es True, imprime información de depuración en la consola.
        
    key: str o None
        Una clave opcional que identifica de manera única este componente.
        Si es None y los argumentos del componente cambian, el componente se
        volverá a montar en el frontend de Streamlit y perderá su estado actual.
    
    Returns
    -------
    str or None
        El token generado por reCAPTCHA si la verificación es exitosa,
        o None si hay un error.
    """
    if debug:
        st.write(f"Inicializando reCAPTCHA con site_key: {site_key}")
        st.write(f"Acción configurada: {action}")
    
    # Call through to our private component function
    component_value = _component_func(
        name=site_key, 
        action=action if action else "default_action", 
        key=key, 
        default=None
    )
    
    if debug and component_value:
        st.write(f"Token recibido (primeros 15 caracteres): {component_value[:15]}...")
    
    return component_value

# Mantener my_component para compatibilidad con versiones anteriores
my_component = recaptcha