import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib";
import React, {
  useEffect,
  useMemo,
  useState,
  ReactElement,
} from "react";
import "./Recaptcha.css";

declare global {
  interface Window {
    grecaptcha: any;
    onReCaptchaLoad: () => void;
  }
}

interface MyComponentProps extends ComponentProps {
  args: {
    name: string; 
    action: string;
  };
}

function MyComponent({
  args,
  disabled,
  theme,
}: MyComponentProps): ReactElement {
  const { name, action } = args;
  
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingState, setLoadingState] = useState<string>("verificando");
  const [scriptLoaded, setScriptLoaded] = useState<boolean>(false);

  useEffect(() => {
    const loadRecaptchaScript = () => {
      const existingScripts = document.querySelectorAll('script[src*="recaptcha"]');
      existingScripts.forEach(script => script.remove());
      
      window.onReCaptchaLoad = () => {
        setScriptLoaded(true);
        setLoadingState("preparando");
      };
      
      const script = document.createElement('script');
      script.src = `https://www.google.com/recaptcha/api.js?render=${name}&onload=onReCaptchaLoad`;
      script.async = true;
      script.defer = true;
      
      script.onerror = () => {
        setError("Error al cargar reCAPTCHA. Verifica tu conexión y la clave del sitio.");
      };
      
      document.head.appendChild(script);
    };
    
    loadRecaptchaScript();
    
    return () => {
      window.onReCaptchaLoad = () => {};
    };
  }, [name]);

  useEffect(() => {
    if (!scriptLoaded) return;
    
    const executeRecaptcha = async () => {
      setLoadingState("analizando");
      
      try {
        if (!window.grecaptcha) {
          setError("Error: API de reCAPTCHA no disponible. Verifica la consola para más detalles.");
          return;
        }
        
        window.grecaptcha.ready(async () => {
          try {
            const token = await window.grecaptcha.execute(name, {action: action});
            
            if (!token) {
              setError("Error: No se pudo generar el token de reCAPTCHA.");
              return;
            }
            
            setCaptchaToken(token);
            setLoadingState("completado");
            Streamlit.setComponentValue(token);
          } catch (err: any) { 
            setError(`Error al verificar: ${err.message || String(err)}`);
          }
        });
      } catch (err: any) { 
        setError(`Error general: ${err.message || String(err)}`);
      }
    };
    
    executeRecaptcha();
  }, [scriptLoaded, name, action]);

  useEffect(() => {
    Streamlit.setFrameHeight(110);
  }, [loadingState, error, captchaToken]);

  const style: React.CSSProperties = useMemo(() => {
    if (!theme) return {};
    return { 
      color: theme.textColor,
      fontFamily: theme.font,
      minHeight: "90px"
    };
  }, [theme]);

  return (
    <div className="recaptcha-container" style={style}>
      {error ? (
        <div className="error-message">
          <div className="recaptcha-icon error-icon">❌</div>
          <div className="recaptcha-text">
            <p><strong>Error de verificación</strong></p>
            <p className="recaptcha-info">{error}</p>
          </div>
        </div>
      ) : captchaToken ? (
        <div className="success-message">
          <div className="recaptcha-icon success-icon">✓</div>
          <div className="recaptcha-text">
            <p><strong>Protegido por reCAPTCHA</strong></p>
            <p className="recaptcha-info">Verificación automática completada</p>
          </div>
          <div className="recaptcha-badge">
            <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Privacidad</a>
            <span className="separator">-</span>
            <a href="https://policies.google.com/terms" target="_blank" rel="noopener noreferrer">Términos</a>
          </div>
        </div>
      ) : (
        <div className="loading-message">
          <div className="recaptcha-icon loading-icon">
            <div className="spinner"></div>
          </div>
          <div className="recaptcha-text">
            <p><strong>Verificando seguridad</strong></p>
            <p className="recaptcha-info">Protegido por reCAPTCHA</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default withStreamlitConnection(MyComponent);