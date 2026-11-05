from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import RolUsuario

class UserCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    especialidad: Optional[str] = "Medicina General"

class UserResponse(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: RolUsuario
    activo: bool
    especialidad: Optional[str] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str
