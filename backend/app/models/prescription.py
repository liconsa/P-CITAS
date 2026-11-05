from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    cita_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    paciente_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fecha_emision = Column(DateTime, default=datetime.now, nullable=False)
    
    diagnostico = Column(Text, nullable=False)
    medicamentos = Column(Text, nullable=False)
    indicaciones = Column(Text, nullable=True)
    folio_receta = Column(String(50), unique=True, index=True, nullable=True)
    cerrada = Column(Boolean, default=False, nullable=False)

    # Relaciones
    cita = relationship("Appointment", back_populates="receta")
    paciente = relationship("User", foreign_keys=[paciente_id])
    medico = relationship("User", foreign_keys=[medico_id])
