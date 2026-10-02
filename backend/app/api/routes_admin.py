from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/admin", tags=["Administrador"])

@router.post("/usuarios", response_model=UserResponse)
def crear_usuario_sistema(usuario: UserCreate, rol: str, db: Session = Depends(get_db)):
    # El administrador podrá registrar, modificar, consultar o administrar los diferentes usuarios del sistema.[cite: 1]
    nuevo_usuario = User(
        nombre=usuario.nombre,
        correo=usuario.correo,
        hashed_password=usuario.password,
        rol=rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.get("/usuarios", response_model=list[UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(User).all()