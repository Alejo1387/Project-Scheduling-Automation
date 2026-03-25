from datetime import datetime, time, timezone, timedelta, date
from app.models.event import Event
from collections import defaultdict
import pytz

# Zona horaria del usuario (Colombia)
USER_TIMEZONE = pytz.timezone("America/Bogota")

def group_events_by_day(events):
    grouped = defaultdict(list)

    for event in events:
        day = event.start.date()
        grouped[day].append(event)

    return grouped

def get_free_slots(events, end_date=None):
    grouped = group_events_by_day(events)
    
    # Asegurar que tenemos todos los días del rango
    if grouped:
        # Comenzar desde hoy
        now = datetime.now(USER_TIMEZONE)
        start_date = now.date()
        
        # Determinar fecha final
        if end_date is None:
            # Por defecto, terminar en el último evento
            last_date = max(e.end.date() for e in events)
        else:
            # Usar la fecha proporcionada
            last_date = end_date.date() if isinstance(end_date, datetime) else end_date
        
        # Generar slots para todos los días desde hoy hasta la fecha final
        current_date = start_date
        while current_date <= last_date:
            if current_date not in grouped:
                grouped[current_date] = []
            current_date += timedelta(days=1)
    else:
        # Si no hay eventos, generar desde hoy hasta fin de mes
        now = datetime.now(USER_TIMEZONE)
        # Calcular último día del mes
        next_month = now.replace(day=28) + timedelta(days=4)
        last_day = (next_month - timedelta(days=next_month.day)).date()
        
        # Generar slots para todos los días
        current_date = now.date()
        while current_date <= last_day:
            grouped[current_date] = []
            current_date += timedelta(days=1)

    free_slots = []

    for day in sorted(grouped.keys()):
        day_events = grouped[day]
        
        # Agregar bloque de almuerzo (12:00 - 13:00)
        lunch_start = datetime.combine(day, time(12, 0), tzinfo=USER_TIMEZONE)
        lunch_end = datetime.combine(day, time(13, 0), tzinfo=USER_TIMEZONE)
        lunch_event = Event(
            id="lunch",
            title="Almuerzo",
            start=lunch_start,
            end=lunch_end
        )
        day_events.append(lunch_event)
        day_events.sort(key=lambda e: e.start)

        start_day = datetime.combine(day, time(9, 0), tzinfo=USER_TIMEZONE)
        end_day = datetime.combine(day, time(17, 0), tzinfo=USER_TIMEZONE)

        current = start_day

        for event in day_events:
            if event.start > current:
                free_slots.append((current, event.start))

            current = max(current, event.end)

        if current < end_day:
            free_slots.append((current, end_day))

    return split_into_30_min_slots(free_slots)

def split_into_30_min_slots(free_slots):
    slots = []

    for start, end in free_slots:
        current = start

        # Mientras haya espacio de 30 min
        while current + timedelta(minutes=30) <= end:
            slot_end = current + timedelta(minutes=30)

            slots.append((current, slot_end))

            # avanzar 30 minutos
            current = slot_end

    return slots