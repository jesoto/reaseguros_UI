import requests
import google.oauth2.id_token
import google.auth.transport.requests
import time

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.token_expiry = 0
    
    def _get_bearer_token(self): 
        request = google.auth.transport.requests.Request()
        target_audience = self.base_url
        id_token = google.oauth2.id_token.fetch_id_token(request, target_audience)
        return id_token
    
    def get_access_token(self):
        if self.token is None or time.time() > self.token_expiry:
            self.token = self._get_bearer_token()
            self.token_expiry = time.time() + 3600  # Assuming the token is valid for 1 hour
        return self.token
    
    def _get_headers(self, is_multipart=False):
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
        }
        # Solo agregamos JSON si NO es un envío de archivos
        if not is_multipart:
            headers['Content-Type'] = 'application/json'
        return headers

    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def post(self, endpoint, json=None,data=None, files=None):
        url = f"{self.base_url}/{endpoint}"
            
        try:
            # Si hay files, usar multipart/form-data
            if files:
                # NO incluir Content-Type en headers, requests lo maneja automáticamente
                headers_copy = {k: v for k, v in self._get_headers().items() if k.lower() != 'content-type'}
                
                response = requests.post(
                    url,
                    files=files,
                    data=data,  # form data adicional (doc-type, etc.)
                    headers=headers_copy,
                    timeout=300  # 5 minutos de timeout para archivos grandes
                )
            # Si no hay files, usar JSON
            elif json:
                response = requests.post(
                    url,
                    json=json,
                    headers=self._get_headers(),
                    timeout=300
                )
            else:
                raise ValueError("Debe proporcionar 'files' o 'json'")

            response.raise_for_status()
            
            return response.json()
        # if response.status_code in [200, 201]:
        #     return response.json()
        # else:
        #     response.raise_for_status()
        
        except Exception as e:
            raise e
    
    def patch(self, endpoint, json):
        url = f"{self.base_url}/{endpoint}"
            
        response = requests.patch(
            url, 
            headers=self._get_headers(), 
            json=json)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            response.raise_for_status()

    def put(self, endpoint, json):
        url = f"{self.base_url}/{endpoint}"
            
        response = requests.put(
            url, 
            headers=self._get_headers(), 
            json=json)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            response.raise_for_status()

    def delete(self, endpoint):
        url = f"{self.base_url}/{endpoint}"

        response = requests.delete(url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @staticmethod
    def _handle_response(response):
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()  # Muestra detalles del error HTTP
