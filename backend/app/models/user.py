from sqlalchemy import Column, Integer, String, Boolean, Enum
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