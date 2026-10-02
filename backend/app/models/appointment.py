from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    estado = Column(String, default="PENDIENTE") # PENDIENTE, CANCELADA, COMPLETADA
    precio = Column(Float, nullable=False)

    # Relaciones ORM
    paciente = relationship("User", foreign_keys=[paciente_id])
    medico = relationship("User", foreign_keys=[medico_id])