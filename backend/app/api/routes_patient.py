from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from app.core.database import get_db

from app.models.appointment import Appointment
from app.models.user import User

from app.schemas.appointment_schema import AppointmentCreate, AppointmentResponse
from app.services.appointment_service import validar_restricciones_cita, CitaPendiente
from app.services.cancellation_policies import procesar_cancelacion_cita, CitaInmutable

router = APIRouter(prefix="/patient", tags=["Paciente"])

# ==========================================
# RUTAS DE EXPEDIENTE CLÍNICO (HISTORY)
# ==========================================

EXPEDIENTE_DB = {}


@router.get("/history")
def obtener_historial(paciente_id: int = 1, db: Session = Depends(get_db)):
    if paciente_id in EXPEDIENTE_DB:
        return EXPEDIENTE_DB[paciente_id]

    return {
        "apellido_paterno": "",
        "apellido_materno": "",
        "nombres": "",
        "curp": "",
        "telefono": "",
        "fecha_nacimiento": "",
        "edad": "",
        "genero": "",
        "lugar_nacimiento": "",
        "calle_numero": "",
        "colonia": "",
        "codigo_postal": "",
        "municipio": "",
        "ant_diabetes": "NO",
        "ant_hipertension": "NO",
        "ant_cardiacos": "NO",
        "blood_type": "",
        "alergias_otro": "",
        "enfermedades_otro": "",
        "discapacidades_otro": "",
        "additional_notes": "",
        "diagnosticos_medicos": ""
    }


@router.post("/history")
def guardar_historial(data: dict, paciente_id: int = 1, db: Session = Depends(get_db)):
    EXPEDIENTE_DB[paciente_id] = data
    return {"mensaje": "Expediente clínico guardado exitosamente"}


# ==========================================
# RUTAS PARA EL FRONTEND (CALENDARIO)
# ==========================================

@router.get("/doctors")
def get_doctors(paciente_id: int = 1, db: Session = Depends(get_db)):
    doctores = db.query(User).filter(User.rol == 'MEDICO').all()

    citas_pendientes = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.estado == "PENDIENTE"
    ).all()

    medicos_con_cita = {c.medico_id for c in citas_pendientes}

    return [{
        "id": d.id,
        "nombre": d.nombre,
        "especialidad": getattr(d, "especialidad", "Medicina General"),
        "tiene_cita_pendiente": d.id in medicos_con_cita
    } for d in doctores]


@router.get("/doctor/{doctor_id}/occupied-days")
def get_occupied_days(doctor_id: int, year: int, month: int, db: Session = Depends(get_db)):
    citas = db.query(Appointment).filter(
        Appointment.medico_id == doctor_id,
        extract('year', Appointment.fecha_hora) == year,
        extract('month', Appointment.fecha_hora) == month,
        Appointment.estado != "CANCELADA"
    ).all()

    conteo_por_dia = {}
    for cita in citas:
        dia = cita.fecha_hora.day
        conteo_por_dia[dia] = conteo_por_dia.get(dia, 0) + 1

    return {"conteo_por_dia": conteo_por_dia}


@router.get("/doctor/{doctor_id}/available-hours")
def get_available_hours(doctor_id: int, date: str, paciente_id: int = 1, db: Session = Depends(get_db)):
    tiene_cita_previa = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.medico_id == doctor_id,
        Appointment.estado == "PENDIENTE"
    ).first()

    if tiene_cita_previa:
        return {"horas": [], "mensaje": "Ya cuentas con una cita pendiente con este médico."}

    fecha_obj = datetime.strptime(date, "%Y-%m-%d").date()
    horarios_base = ["09:00", "10:30", "12:00", "13:30", "15:00", "16:30"]

    citas_del_dia = db.query(Appointment).filter(
        Appointment.medico_id == doctor_id,
        extract('year', Appointment.fecha_hora) == fecha_obj.year,
        extract('month', Appointment.fecha_hora) == fecha_obj.month,
        extract('day', Appointment.fecha_hora) == fecha_obj.day,
        Appointment.estado != "CANCELADA"
    ).all()

    horas_ocupadas = [cita.fecha_hora.strftime("%H:%M") for cita in citas_del_dia]
    horas_disponibles = [h for h in horarios_base if h not in horas_ocupadas]
    return {"horas": horas_disponibles}


# ==========================================
# RUTAS DE CITAS (AGENDAR, CANCELAR, HISTORIAL)
# ==========================================

@router.post("/citas", response_model=AppointmentResponse)
def agendar_cita(cita_in: AppointmentCreate, paciente_id: int = 1, db: Session = Depends(get_db)):
    # Validación 1: Médico ocupado
    medico_ocupado = db.query(Appointment).filter(
        Appointment.medico_id == cita_in.medico_id,
        Appointment.fecha_hora == cita_in.fecha_hora,
        Appointment.estado != "CANCELADA"
    ).first()

    if medico_ocupado:
        raise HTTPException(
            status_code=400,
            detail="El horario seleccionado ya no se encuentra disponible para este médico."
        )

    # Validación 2: Paciente ocupado a la misma hora con otro doctor
    paciente_ocupado = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.fecha_hora == cita_in.fecha_hora,
        Appointment.estado != "CANCELADA"
    ).first()

    if paciente_ocupado:
        raise HTTPException(
            status_code=400,
            detail="Ya tienes otra cita agendada en este mismo horario con otro médico."
        )

    citas_db = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.estado == "PENDIENTE"
    ).all()

    citas_pendientes = [CitaPendiente(medico_id=c.medico_id, estado=c.estado) for c in citas_db]

    error = validar_restricciones_cita(cita_in.fecha_hora, cita_in.medico_id, citas_pendientes)
    if error:
        raise HTTPException(status_code=400, detail=error)

    nueva_cita = Appointment(
        paciente_id=paciente_id,
        medico_id=cita_in.medico_id,
        fecha_hora=cita_in.fecha_hora,
        precio=500.00
    )
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


@router.post("/citas/{cita_id}/cancelar")
def cancelar_cita_paciente(cita_id: int, db: Session = Depends(get_db)):
    cita_db = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita_db:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita_inmutable = CitaInmutable(
        id=cita_db.id,
        fecha=cita_db.fecha_hora,
        precio=cita_db.precio,
        estado=cita_db.estado
    )

    cita_cancelada, reembolso = procesar_cancelacion_cita(cita_inmutable, datetime.now())

    cita_db.estado = cita_cancelada.estado
    db.commit()

    return {
        "mensaje": "Cita cancelada exitosamente",
        "estado": cita_cancelada.estado,
        "reembolso_calculado": reembolso
    }


@router.get("/citas")
def consultar_historial(paciente_id: int = 1, db: Session = Depends(get_db)):
    resultados = db.query(Appointment, User).join(
        User, Appointment.medico_id == User.id
    ).filter(
        Appointment.paciente_id == paciente_id
    ).all()

    citas_con_detalles = []
    for cita, medico in resultados:
        citas_con_detalles.append({
            "id": cita.id,
            "paciente_id": cita.paciente_id,
            "medico_id": cita.medico_id,
            "fecha_hora": cita.fecha_hora,
            "precio": cita.precio,
            "estado": cita.estado,
            "medico_nombre": medico.nombre,
            "medico_especialidad": getattr(medico, "especialidad", "Medicina General")
        })

    return citas_con_detalles