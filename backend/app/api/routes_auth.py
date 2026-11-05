from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserResponse, LoginRequest
from app.models.user import User, RolUsuario
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configuración JWT (Para un proyecto escolar, esto es suficiente)
SECRET_KEY = "clave_secreta_hospital_escom"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Extrae el usuario actual a partir del token de la petición"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


@router.post("/registro", response_model=UserResponse)
def registrar_paciente(usuario: UserCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(User).filter(User.correo == usuario.correo).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    nuevo_usuario = User(
        nombre=usuario.nombre,
        correo=usuario.correo,
        hashed_password=usuario.password,  # Nota: Sin encriptar por ahora para no romper tu BD
        rol=RolUsuario.PACIENTE,
        activo=True
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

    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Esta cuenta se encuentra inactiva.")

    # Generamos el token REAL con el ID del usuario
    token_data = {"sub": str(usuario.id)}
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": usuario.rol.value,
        "user": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "rol": usuario.rol.value,
            "especialidad": getattr(usuario, "especialidad", None)
        }
    }