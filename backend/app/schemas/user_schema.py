from pydantic import BaseModel, EmailStr
from app.models.user import RolUsuario

class UserCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: RolUsuario
    activo: bool

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str