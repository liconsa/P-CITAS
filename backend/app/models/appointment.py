from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    estado = Column(String, default="PENDIENTE")  # PENDIENTE, PAGADA, CANCELADA, COMPLETADA
    precio = Column(Float, nullable=False, default=500.0)
    folio_pago = Column(String, nullable=True, unique=True, index=True)
    jornada_id = Column(Integer, ForeignKey("jornadas.id"), nullable=True)

    # Relaciones ORM
    paciente = relationship("User", foreign_keys=[paciente_id])
    medico = relationship("User", foreign_keys=[medico_id])
    jornada = relationship("Jornada", back_populates="cita")
    receta = relationship("Prescription", back_populates="cita", uselist=False, cascade="all, delete-orphan")
