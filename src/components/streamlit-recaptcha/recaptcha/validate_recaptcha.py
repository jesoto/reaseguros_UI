import requests
import json
import logging

logger = logging.getLogger(__name__)

def validate_recaptcha_token(token, action, site_key, api_key, project_id):
    url = f"https://recaptchaenterprise.googleapis.com/v1/projects/{project_id}/assessments?key={api_key}"
    
    payload = {
        "event": {
            "token": token,
            "expectedAction": action,
            "siteKey": site_key
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al validar token de reCAPTCHA: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Código de estado: {e.response.status_code}")
            logger.error(f"Respuesta: {e.response.text}")
        return None

def interpret_recaptcha_response(response, score_threshold=0.5):
    if not response:
        return False, 0, ["Error en la respuesta de la API"]
    
    try:
        is_valid = response.get("tokenProperties", {}).get("valid", False)
        score = response.get("riskAnalysis", {}).get("score", 0)
        action_match = response.get("tokenProperties", {}).get("action", "") == response.get("event", {}).get("expectedAction", "")
        
        reasons = []
        
        if not is_valid:
            reasons.append("Token no válido")
            invalid_reason = response.get("tokenProperties", {}).get("invalidReason", "")
            if invalid_reason:
                reasons.append(f"Razón: {invalid_reason}")
        
        if not action_match:
            reasons.append("La acción no coincide con la esperada")
        
        if score < score_threshold:
            reasons.append(f"Puntuación ({score}) por debajo del umbral mínimo ({score_threshold})")
        
        is_human = is_valid and action_match and score >= score_threshold
        
        return is_human, score, reasons
        
    except Exception as e:
        logger.error(f"Error al interpretar respuesta de reCAPTCHA: {str(e)}")
        return False, 0, [f"Error al procesar la respuesta: {str(e)}"]