from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
import pytz

from app.services.calendar_service import list_events
from app.services.availability_service import get_free_slots

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