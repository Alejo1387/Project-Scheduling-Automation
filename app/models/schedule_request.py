from pydantic import BaseModel, Field
from datetime import datetime

class ScheduleRequest(BaseModel):
    start: datetime = Field(..., description="Fecha y hora de inicio del evento")
    end: datetime = Field(..., description="Fecha y hora de finalización del evento")
    title: str = Field(..., min_length=1, max_length=200, description="Título del evento")