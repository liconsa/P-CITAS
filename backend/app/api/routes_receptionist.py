from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.jornada import Jornada
from app.models.user import User, RolUsuario
from app.api.routes_auth import get_current_user

router = APIRouter(prefix="/receptionist", tags=["Recepcionista"])


# ==========================================
# RUTAS DE LECTURA (PARA QUE CARGUE LA VISTA)
# ==========================================

@router.get("/appointments-all")
def listar_todas_las_citas(usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    citas = db.query(Appointment).all()
    resultado = []
    for c in citas:
        paciente = db.query(User).filter(User.id == c.paciente_id).first()
        medico = db.query(User).filter(User.id == c.medico_id).first()
        resultado.append({
            "id": c.id,
            "paciente_id": c.paciente_id,
            "medico_id": c.medico_id,
            "paciente_nombre": paciente.nombre if paciente else "N/D",
            "medico_nombre": medico.nombre if medico else "N/D",
            "fecha_hora": c.fecha_hora,
            "precio": c.precio,
            "estado": c.estado,
            "folio_pago": c.folio_pago
        })
    return resultado


@router.get("/appointments")
def listar_citas_alternativa(usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return listar_todas_las_citas(usuario_actual, db)


@router.get("/doctors-admin")
def listar_doctores_admin(usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doctores = db.query(User).filter(User.rol == RolUsuario.MEDICO).all()
    return [{
        "id": d.id,
        "nombre": d.nombre,
        "email": getattr(d, "email", getattr(d, "username", "N/D")), # Validación segura para evitar el error
        "activo": getattr(d, "activo", True),
        "especialidad": getattr(d.perfil_medico, "especialidad", "Medicina General") if getattr(d, "perfil_medico", None) else "Medicina General"
    } for d in doctores]


# ==========================================
# RUTAS DE ACCIÓN
# ==========================================

@router.post("/appointments/{cita_id}/cancel")
def recepcionista_cancelar_cita(cita_id: int, usuario_actual: User = Depends(get_current_user),
                                db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")

    cita.estado = "CANCELADA"

    jornada = db.query(Jornada).filter(
        Jornada.medico_id == cita.medico_id,
        Jornada.fecha_hora == cita.fecha_hora
    ).first()
    if jornada:
        jornada.estado = "DISPONIBLE"

    db.commit()
    return {"mensaje": "Cita cancelada y reembolso procesado por recepción."}


@router.post("/doctors/{doctor_id}/toggle-status")
def cambiar_estado_doctor(doctor_id: int, usuario_actual: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    doctor = db.query(User).filter(User.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Médico no encontrado.")

    estado_actual = getattr(doctor, "activo", True)
    doctor.activo = not estado_actual

    citas_afectadas = 0
    if not doctor.activo:
        citas_activas = db.query(Appointment).filter(
            Appointment.medico_id == doctor_id,
            Appointment.estado.in_(["PENDIENTE", "PAGADA", "PAGADO"])
        ).all()

        for cita in citas_activas:
            cita.estado = "CANCELADA"
            citas_afectadas += 1

            jornada = db.query(Jornada).filter(
                Jornada.medico_id == doctor_id,
                Jornada.fecha_hora == cita.fecha_hora
            ).first()
            if jornada:
                jornada.estado = "DISPONIBLE"

    db.commit()

    estado_texto = "activo" if doctor.activo else "dado de baja temporalmente"
    return {
        "mensaje": f"El médico ha sido {estado_texto}. Se cancelaron y reembolsaron {citas_afectadas} citas asociadas.",
        "activo": doctor.activo
    }