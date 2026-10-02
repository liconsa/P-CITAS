from pydantic import BaseModel
from datetime import datetime

class AppointmentCreate(BaseModel):
    medico_id: int
    fecha_hora: datetime

class AppointmentResponse(BaseModel):
    id: int
    medico_id: int
    paciente_id: int
    fecha_hora: datetime
    estado: str
    precio: float

    class Config:
        from_attributes = True