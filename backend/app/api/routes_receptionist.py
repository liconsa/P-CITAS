from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
# 👈 CAMBIO AQUÍ: Importamos el User, el DoctorProfile y tu Enum RolUsuario
from app.models.user import User, DoctorProfile, RolUsuario
from app.models.appointment import Appointment
from datetime import datetime

router = APIRouter(prefix="/receptionist", tags=["Recepcionista"])


# ==========================================
# 1. GESTIÓN DE MÉDICOS (Altas y Bajas)
# ==========================================

@router.get("/doctors-admin")
def listar_todos_los_medicos(db: Session = Depends(get_db)):
    # 👈 CAMBIO AQUÍ: Filtramos usando el Enum de SQLAlchemy
    medicos = db.query(User).filter(User.rol == RolUsuario.MEDICO).all()
    resultado = []
    for m in medicos:
        # 👈 CAMBIO AQUÍ: Buscamos la especialidad en la tabla relacionada (perfil_medico)
        especialidad_asignada = m.perfil_medico.especialidad if getattr(m, "perfil_medico",
                                                                        None) else "Sin especialidad"

        resultado.append({
            "id": m.id,
            "nombre": m.nombre,
            "email": getattr(m, "correo", "Sin correo"),
            "especialidad": especialidad_asignada,
            "activo": getattr(m, "activo", True)
        })
    return resultado


@router.post("/doctors-register")
def dar_de_alta_medico(data: dict, db: Session = Depends(get_db)):
    # 👈 CAMBIO AQUÍ: 1. Creamos el registro en la tabla general de Usuarios
    nuevo_usuario = User(
        nombre=data.get("nombre"),
        correo=data.get("email"),
        hashed_password=data.get("password"),  # Guardamos la contraseña en la columna correcta
        rol=RolUsuario.MEDICO,  # Usamos el Enum correspondiente
        activo=True
    )
    db.add(nuevo_usuario)
    db.flush()  # Guardamos temporalmente para que la BD le asigne un ID (nuevo_usuario.id)

    # 👈 CAMBIO AQUÍ: 2. Creamos el registro en la tabla DoctorProfile usando ese ID
    nuevo_perfil = DoctorProfile(
        user_id=nuevo_usuario.id,
        especialidad=data.get("especialidad", "Medicina General")
    )
    db.add(nuevo_perfil)

    # Confirmamos ambas transacciones juntas
    db.commit()
    db.refresh(nuevo_usuario)

    return {"mensaje": "Médico registrado con éxito", "id": nuevo_usuario.id}


@router.post("/doctors/{medico_id}/toggle-status")
def cambiar_estado_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(User).filter(User.id == medico_id, User.rol == RolUsuario.MEDICO).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    medico.activo = not getattr(medico, "activo", True)
    db.commit()
    return {"mensaje": f"Estado del médico actualizado correctamente. Activo: {medico.activo}"}


# ==========================================
# 2. GESTIÓN DE CITAS (Confirmación y Cancelación)
# ==========================================

@router.get("/appointments-all")
def listar_todas_las_citas(db: Session = Depends(get_db)):
    citas = db.query(Appointment).all()
    resultado = []
    for c in citas:
        paciente = db.query(User).filter(User.id == c.paciente_id).first()
        medico = db.query(User).filter(User.id == c.medico_id).first()

        resultado.append({
            "id": c.id,
            "paciente_nombre": paciente.nombre if paciente else f"Paciente #{c.paciente_id}",
            "medico_nombre": medico.nombre if medico else f"Médico #{c.medico_id}",
            "fecha_hora": c.fecha_hora,
            "estado": c.estado,
            "precio": c.precio
        })
    return resultado


@router.post("/appointments/{cita_id}/confirmar")
def confirmar_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "CONFIRMADA"
    db.commit()
    return {"mensaje": "Cita confirmada exitosamente"}


@router.post("/appointments/{cita_id}/cancelar")
def cancelar_cita_recepcion(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "CANCELADA"
    db.commit()
    return {"mensaje": "Cita cancelada por la recepcionista"}