from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class RolUsuario(str, enum.Enum):
    ADMIN = "administrador"
    RECEPCIONISTA = "recepcionista"
    MEDICO = "medico"
    PACIENTE = "paciente"
    CAJERO = "cajero" # Incluido según los requerimientos

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    correo = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(Enum(RolUsuario), nullable=False)
    activo = Column(Boolean, default=True)

    # Relación "Uno a Uno" con el perfil del médico
    perfil_medico = relationship("DoctorProfile", back_populates="usuario", uselist=False)

# 🌟 NUEVA TABLA: Solo existe si el usuario es Médico
class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True) # Vinculado al User
    especialidad = Column(String, nullable=False, default="Medicina General")

    # Relación de vuelta al usuario
    usuario = relationship("User", back_populates="perfil_medico")