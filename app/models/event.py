from pydantic import BaseModel
from datetime import datetime


class Event(BaseModel):
    id: str | None = None
    title: str | None = None
    start: datetime
    end: datetime