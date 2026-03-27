from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta, timezone
import pytz

from app.services.calendar_service import list_events
from app.services.availability_service import get_free_slots

from app.models.schedule_request import ScheduleRequest
from app.services.calendar_service import create_event

# Zona horaria del usuario (Colombia)
USER_TIMEZONE = pytz.timezone("America/Bogota")

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/events")
def get_events():
    events = list_events()
    return events

@router.get("/availability")
def availability(days: int | None = Query(None)):
    events = list_events()
    
    now = datetime.now(USER_TIMEZONE)

    # 🔹 Si NO envían days → usar fin de mes
    if days is None:
        # ir al día 28
        next_month = now.replace(day=28) + timedelta(days=4)

        # restar para llegar al último día del mes actual
        end_of_month = next_month - timedelta(days=next_month.day)

        # poner hora final del día
        limit = end_of_month.replace(
            hour=23,
            minute=59,
            second=59
        )
    else:
        # si envían days → usar rango normal
        limit = now + timedelta(days=days)

    # Pasar el límite a get_free_slots para generar slots hasta esa fecha
    free_slots = get_free_slots(events, end_date=limit)

    filtered = [
        slot for slot in free_slots
        if slot[0] >= now and slot[0] <= limit
    ]

    return [
        {
            "start": s.isoformat(),
            "end": e.isoformat()
        }
        for s, e in filtered
    ]

@router.post("/schedule")
def schedule(request: ScheduleRequest):
    """
    Crea un evento en el calendario validando que el horario esté disponible.
    """
    try:
        # 🔹 Validar entrada básica
        if not request.title or request.title.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="El título del evento no puede estar vacío"
            )
        
        if request.start >= request.end:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio debe ser anterior a la fecha de finalización"
            )
        
        # 🔹 Asegurar que las fechas tienen zona horaria de Colombia
        start = request.start
        end = request.end
        
        if start.tzinfo is None:
            start = start.replace(tzinfo=USER_TIMEZONE)
        
        if end.tzinfo is None:
            end = end.replace(tzinfo=USER_TIMEZONE)
        
        # 🔹 Recalcular disponibilidad
        events = list_events()
        free_slots = get_free_slots(events)
        
        requested_slot = (start, end)
        
        # 🔹 Verificar si el slot sigue libre
        if requested_slot not in free_slots:
            raise HTTPException(
                status_code=409,
                detail="Ese horario ya no está disponible"
            )
        
        # 🔹 Crear evento
        created_event = create_event(
            start=start,
            end=end,
            title=request.title.strip()
        )
        
        return {
            "message": "Evento creado exitosamente",
            "event_id": created_event.get("id"),
            "title": created_event.get("summary"),
            "start": created_event.get("start").get("dateTime"),
            "end": created_event.get("end").get("dateTime")
        }
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el evento: {str(e)}"
        )