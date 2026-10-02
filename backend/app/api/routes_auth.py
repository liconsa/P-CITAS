from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserResponse, LoginRequest
from app.models.user import User, RolUsuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UserResponse)
def registrar_paciente(usuario: UserCreate, db: Session = Depends(get_db)):
    # Un paciente puede registrarse dentro del sistema.[cite: 1]
    usuario_existente = db.query(User).filter(User.correo == usuario.correo).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    nuevo_usuario = User(
        nombre=usuario.nombre,
        correo=usuario.correo,
        hashed_password=usuario.password,  # Nota: Implementar bcrypt o similar para producción
        rol=RolUsuario.PACIENTE
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login")
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.correo == credenciales.correo).first()

    if not usuario or usuario.hashed_password != credenciales.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {
        "access_token": "token_jwt_generado_aqui",
        "token_type": "bearer",
        "rol": usuario.rol.value
    }