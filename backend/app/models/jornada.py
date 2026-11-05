from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Date, Time
from sqlalchemy.orm import relationship
from app.core.database import Base

class Jornada(Base):
    __tablename__ = "jornadas"

    id = Column(Integer, primary_key=True, index=True)
    medico_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    fecha_hora = Column(DateTime, nullable=False, index=True)
    duracion_minutos = Column(Integer, default=60, nullable=False)
    # Estados: DISPONIBLE, PENDIENTE, PAGADO, BLOQUEADO
    estado = Column(String, default="DISPONIBLE", nullable=False)
    asignado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relaciones ORM
    medico = relationship("User", foreign_keys=[medico_id])
    asignado_por = relationship("User", foreign_keys=[asignado_por_id])
    cita = relationship("Appointment", back_populates="jornada", uselist=False)

    @property
    def medico_nombre(self):
        return self.medico.nombre if self.medico else None
