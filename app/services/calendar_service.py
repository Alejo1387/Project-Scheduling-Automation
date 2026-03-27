from app.clients.google_calendar_client import get_calendar_service
from app.models.event import Event
from datetime import datetime, timezone, timedelta
import pytz


# Zona horaria del usuario (Colombia)
USER_TIMEZONE = pytz.timezone("America/Bogota")


def normalize_event(google_event: dict) -> Event:
    start = google_event["start"].get("dateTime") or google_event["start"].get("date")
    end = google_event["end"].get("dateTime") or google_event["end"].get("date")

    # Convertir a datetime
    # Si es una fecha simple (all-day event), convertir a datetime
    if "T" not in start:  # Es una fecha simple (YYYY-MM-DD)
        start = f"{start}T00:00:00Z"
    if "T" not in end:
        end = f"{end}T00:00:00Z"
    
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

    # SOLUCIÓN CLAVE: forzar timezone si no existe
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)

    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    
    # Convertir a la zona horaria del usuario (Colombia)
    start_dt = start_dt.astimezone(USER_TIMEZONE)
    end_dt = end_dt.astimezone(USER_TIMEZONE)

    return Event(
        id=google_event.get("id"),
        title=google_event.get("summary"),
        start=start_dt,
        end=end_dt,
    )


def list_events():
    service = get_calendar_service()

    now = datetime.now(USER_TIMEZONE)

    end_of_year = datetime(
        year=now.year,
        month=12,
        day=31,
        hour=23,
        minute=59,
        second=59,
        tzinfo=USER_TIMEZONE
    )

    # Convertir a UTC para la API de Google
    now_utc = now.astimezone(timezone.utc)
    end_of_year_utc = end_of_year.astimezone(timezone.utc)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now_utc.isoformat(),
        timeMax=end_of_year_utc.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    google_events = events_result.get("items", [])

    normalized_events = [normalize_event(e) for e in google_events]

    return normalized_events

def create_event(start: datetime, end: datetime, title: str):
    """
    Crea un evento en Google Calendar.
    
    Args:
        start: Fecha/hora de inicio en zona horaria de Colombia
        end: Fecha/hora de finalización en zona horaria de Colombia
        title: Título del evento
        
    Returns:
        El evento creado con su ID
        
    Raises:
        ValueError: Si las fechas son inválidas
        Exception: Si hay error al conectar con Google Calendar
    """
    try:
        # Validar que start sea antes que end
        if start >= end:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de finalización")
        
        # Si las fechas no tienen zona horaria, asignar la de Colombia
        if start.tzinfo is None:
            start = start.replace(tzinfo=USER_TIMEZONE)
        
        if end.tzinfo is None:
            end = end.replace(tzinfo=USER_TIMEZONE)
        
        # Convertir a UTC para enviar a Google Calendar
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        
        service = get_calendar_service()

        event = {
            "summary": title,
            "start": {
                "dateTime": start_utc.isoformat(),
                "timeZone": "America/Bogota",
            },
            "end": {
                "dateTime": end_utc.isoformat(),
                "timeZone": "America/Bogota",
            },
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()
        
        # Validar que el evento se creó correctamente
        if not created_event.get("id"):
            raise Exception("El evento no se creó correctamente en Google Calendar")

        return created_event
        
    except ValueError as ve:
        raise ValueError(f"Error de validación: {str(ve)}")
    except Exception as e:
        raise Exception(f"Error al crear el evento en Google Calendar: {str(e)}")