from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User, DoctorProfile, RolUsuario
from app.models.jornada import Jornada
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.appointment_schema import JornadaCreate, JornadaBatchCreate, JornadaResponse

router = APIRouter(prefix="/admin", tags=["Administrador"])

# ==========================================
# GESTIÓN DE USUARIOS
# ==========================================

@router.post("/usuarios", response_model=UserResponse)
def crear_usuario_sistema(data: dict, db: Session = Depends(get_db)):
    """
    Crea un usuario del sistema (Médico o Recepcionista) recibiendo los datos por JSON corporativo.
    """
    nombre = data.get("nombre")
    correo = data.get("correo")
    password = data.get("password")
    rol_input = str(data.get("rol", "MEDICO")).strip().upper()
    especialidad = data.get("especialidad", "Medicina General")

    if not nombre or not correo or not password:
        raise HTTPException(status_code=400, detail="Faltan campos obligatorios (nombre, correo, contraseña).")

    existente = db.query(User).filter(User.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado.")

    # Mapeo exacto del rol enviado desde el select de Angular
    if "RECEPCION" in rol_input:
        rol_val = RolUsuario.RECEPCIONISTA
    else:
        rol_val = RolUsuario.MEDICO

    nuevo_usuario = User(
        nombre=nombre,
        correo=correo,
        hashed_password=password,
        rol=rol_val
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Si es médico, asignamos su perfil de especialidad médica
    if rol_val == RolUsuario.MEDICO:
        perfil = DoctorProfile(
            user_id=nuevo_usuario.id,
            especialidad=especialidad or "Medicina General"
        )
        db.add(perfil)
        db.commit()
        db.refresh(nuevo_usuario)

    return nuevo_usuario

@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(User).order_by(User.id.asc()).all()
    return [{
        "id": u.id,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol.value if hasattr(u.rol, "value") else u.rol
    } for u in usuarios]

@router.get("/medicos")
def listar_medicos_admin(db: Session = Depends(get_db)):
    medicos = db.query(User).filter(User.rol == RolUsuario.MEDICO).all()
    return [{
        "id": m.id,
        "nombre": m.nombre,
        "correo": m.correo,
        "especialidad": m.especialidad or "Medicina General"
    } for m in medicos]

@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente."}


# ==========================================
# GESTIÓN DE JORNADAS LABORALES (POSTULACIONES/HORARIOS)
# ==========================================

@router.post("/jornadas/batch", response_model=List[JornadaResponse])
def asignar_jornadas_lote(datos: JornadaBatchCreate, admin_id: int = 1, db: Session = Depends(get_db)):
    medico = db.query(User).filter(User.id == datos.medico_id, User.rol == RolUsuario.MEDICO).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado o rol inválido.")

    jornadas_creadas = []
    for hora_str in datos.horas:
        try:
            fecha_hora_str = f"{datos.fecha} {hora_str}"
            dt_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Formato de hora o fecha inválido: {datos.fecha} {hora_str}")

        existente = db.query(Jornada).filter(
            Jornada.medico_id == datos.medico_id,
            Jornada.fecha_hora == dt_obj
        ).first()

        if not existente:
            nueva_jornada = Jornada(
                medico_id=datos.medico_id,
                fecha_hora=dt_obj,
                duracion_minutos=datos.duracion_minutos,
                estado="DISPONIBLE",
                asignado_por_id=admin_id
            )
            db.add(nueva_jornada)
            jornadas_creadas.append(nueva_jornada)

    db.commit()
    for j in jornadas_creadas:
        db.refresh(j)

    return jornadas_creadas


@router.post("/jornadas", response_model=JornadaResponse)
def asignar_jornada_individual(datos: JornadaCreate, admin_id: int = 1, db: Session = Depends(get_db)):
    medico = db.query(User).filter(User.id == datos.medico_id, User.rol == RolUsuario.MEDICO).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado.")

    existente = db.query(Jornada).filter(
        Jornada.medico_id == datos.medico_id,
        Jornada.fecha_hora == datos.fecha_hora
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una jornada asignada para este médico en ese horario.")

    nueva = Jornada(
        medico_id=datos.medico_id,
        fecha_hora=datos.fecha_hora,
        duracion_minutos=datos.duracion_minutos,
        estado="DISPONIBLE",
        asignado_por_id=admin_id
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get("/jornadas", response_model=List[JornadaResponse])
def listar_jornadas(
    medico_id: Optional[int] = None,
    fecha: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Jornada)
    if medico_id:
        query = query.filter(Jornada.medico_id == medico_id)
    if fecha:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        query = query.filter(
            db.func.date(Jornada.fecha_hora) == fecha_obj
        )
    return query.order_by(Jornada.fecha_hora.desc()).all()


@router.delete("/jornadas/{jornada_id}")
def eliminar_jornada(jornada_id: int, db: Session = Depends(get_db)):
    query = db.query(Jornada).filter(Jornada.id == jornada_id)
    jornada = query.first()
    if not jornada:
        raise HTTPException(status_code=404, detail="Jornada no encontrada.")

    if jornada.estado != "DISPONIBLE":
        raise HTTPException(status_code=400, detail="No se puede eliminar una jornada que está reservada o pagada.")

    db.delete(jornada)
    db.commit()
    return {"mensaje": "Jornada eliminada correctamente."}