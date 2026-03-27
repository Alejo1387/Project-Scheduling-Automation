from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "client_secret.json"


def get_calendar_service():
    """
    Obtiene el servicio de Google Calendar.
    Si existen credenciales guardadas, las usa sin pedir autenticación.
    Si no existen o están expiradas, pide autenticación una sola vez y las guarda.
    """
    creds = None
    
    # Si existe el archivo de token guardado, cargarlo
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, hacer autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Si el token expiró pero tenemos refresh token, renovarlo
            creds.refresh(Request())
        else:
            # Hacer autenticación desde cero
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Guardar las credenciales para futuras ejecuciones
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service