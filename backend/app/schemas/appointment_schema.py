from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AppointmentCreate(BaseModel):
    medico_id: int
    fecha_hora: datetime
    paciente_id: Optional[int] = None

class AppointmentPayment(BaseModel):
    folio_pago: Optional[str] = None
    metodo_pago: Optional[str] = "SIMULADO"

class AppointmentResponse(BaseModel):
    id: int
    medico_id: int
    paciente_id: int
    fecha_hora: datetime
    estado: str
    precio: float
    folio_pago: Optional[str] = None
    jornada_id: Optional[int] = None

    class Config:
        from_attributes = True

class JornadaCreate(BaseModel):
    medico_id: int
    fecha_hora: datetime
    duracion_minutos: int = 60

class JornadaBatchCreate(BaseModel):
    medico_id: int
    fecha: str  # YYYY-MM-DD
    horas: List[str]  # ["09:00", "10:30", ...]
    duracion_minutos: int = 60

class JornadaResponse(BaseModel):
    id: int
    medico_id: int
    fecha_hora: datetime
    duracion_minutos: int
    estado: str
    medico_nombre: Optional[str] = None

    class Config:
        from_attributes = True

class PrescriptionCreate(BaseModel):
    cita_id: int
    diagnostico: str
    medicamentos: str
    indicaciones: Optional[str] = None

class PrescriptionResponse(BaseModel):
    id: int
    cita_id: int
    paciente_id: int
    medico_id: int
    fecha_emision: datetime
    diagnostico: str
    medicamentos: str
    indicaciones: Optional[str] = None
    folio_receta: Optional[str] = None
    cerrada: bool
    paciente_nombre: Optional[str] = None
    medico_nombre: Optional[str] = None
    medico_especialidad: Optional[str] = None

    class Config:
        from_attributes = True
