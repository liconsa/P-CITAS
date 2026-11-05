from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime, date, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.jornada import Jornada
from app.models.user import User, RolUsuario
from app.api.routes_auth import get_current_user

from app.schemas.appointment_schema import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentPayment
)
from app.services.appointment_service import (
    validar_restricciones_cita,
    CitaPendiente,
    SlotJornada,
    validar_disponibilidad_jornada
)
from app.services.cancellation_policies import (
    procesar_cancelacion_cita,
    es_cita_cancelable,
    generar_folio_pago,
    CitaInmutable
)

router = APIRouter(prefix="/patient", tags=["Paciente"])

EXPEDIENTE_DB = {}


@router.get("/history")
def obtener_historial(usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paciente_id = usuario_actual.id
    if paciente_id in EXPEDIENTE_DB:
        return EXPEDIENTE_DB[paciente_id]
    return {
        "apellido_paterno": "", "apellido_materno": "", "nombres": "", "curp": "", "telefono": "",
        "fecha_nacimiento": "", "edad": "", "genero": "", "lugar_nacimiento": "", "calle_numero": "",
        "colonia": "", "codigo_postal": "", "municipio": "", "ant_diabetes": "NO", "ant_hipertension": "NO",
        "ant_cardiacos": "NO", "blood_type": "", "alergias_otro": "", "enfermedades_otro": "",
        "discapacidades_otro": "", "additional_notes": "", "diagnosticos_medicos": ""
    }


@router.post("/history")
def guardar_historial(data: dict, usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paciente_id = usuario_actual.id
    EXPEDIENTE_DB[paciente_id] = data
    return {"mensaje": "Expediente clínico guardado exitosamente"}


@router.get("/doctors")
def get_doctors(usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paciente_id = usuario_actual.id

    doctores = db.query(User).filter(
        User.rol == RolUsuario.MEDICO,
        (User.activo == True) | (User.activo == None)
    ).all()

    citas_activas = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.estado.in_(["PENDIENTE", "PAGADA", "PAGADO"])
    ).all()
    medicos_con_cita = {c.medico_id for c in citas_activas}

    return [{
        "id": d.id,
        "nombre": d.nombre,
        "especialidad": getattr(d.perfil_medico, "especialidad", "Medicina General") if getattr(
            d, "perfil_medico", None) else "Medicina General",
        "tiene_cita_pendiente": d.id in medicos_con_cita
    } for d in doctores]


@router.get("/doctor/{doctor_id}/occupied-days")
def get_occupied_days(doctor_id: int, year: int, month: int, db: Session = Depends(get_db)):
    jornadas = db.query(Jornada).filter(
        Jornada.medico_id == doctor_id,
        extract('year', Jornada.fecha_hora) == year,
        extract('month', Jornada.fecha_hora) == month,
        Jornada.estado.in_(["PENDIENTE", "PAGADO"])
    ).all()
    conteo_por_dia = {}
    for j in jornadas:
        dia = j.fecha_hora.day
        conteo_por_dia[dia] = conteo_por_dia.get(dia, 0) + 1
    return {"conteo_por_dia": conteo_por_dia}


@router.get("/doctor/{doctor_id}/available-hours")
def get_available_hours(doctor_id: int, date: str, usuario_actual: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    paciente_id = usuario_actual.id
    tiene_cita_previa = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.medico_id == doctor_id,
        Appointment.estado.in_(["PENDIENTE", "PAGADA", "PAGADO"])
    ).first()
    if tiene_cita_previa:
        return {"horas": [], "mensaje": "Ya cuentas con una cita pendiente o pagada con este médico."}

    fecha_obj = datetime.strptime(date, "%Y-%m-%d").date()
    jornadas_dia = db.query(Jornada).filter(
        Jornada.medico_id == doctor_id,
        extract('year', Jornada.fecha_hora) == fecha_obj.year,
        extract('month', Jornada.fecha_hora) == fecha_obj.month,
        extract('day', Jornada.fecha_hora) == fecha_obj.day
    ).order_by(Jornada.fecha_hora.asc()).all()

    if not jornadas_dia:
        horarios_base = ["09:00", "10:30", "12:00", "13:30", "15:00", "16:30"]
        for h_str in horarios_base:
            h_dt = datetime.combine(fecha_obj, datetime.strptime(h_str, "%H:%M").time())
            db.add(Jornada(medico_id=doctor_id, fecha_hora=h_dt, duracion_minutos=60, estado="DISPONIBLE"))
        db.commit()
        jornadas_dia = db.query(Jornada).filter(
            Jornada.medico_id == doctor_id,
            extract('year', Jornada.fecha_hora) == fecha_obj.year,
            extract('month', Jornada.fecha_hora) == fecha_obj.month,
            extract('day', Jornada.fecha_hora) == fecha_obj.day
        ).order_by(Jornada.fecha_hora.asc()).all()

    horas_disponibles = [j.fecha_hora.strftime("%H:%M") for j in jornadas_dia if j.estado == "DISPONIBLE"]
    return {"horas": horas_disponibles}


@router.post("/citas", response_model=AppointmentResponse)
def agendar_cita(cita_in: AppointmentCreate, usuario_actual: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    paciente_id = usuario_actual.id
    ahora = datetime.now()

    paciente_ocupado = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.fecha_hora == cita_in.fecha_hora,
        Appointment.estado != "CANCELADA"
    ).first()
    if paciente_ocupado:
        raise HTTPException(status_code=400,
                            detail="Ya tienes otra cita agendada en este mismo horario con otro médico.")

    citas_db = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.estado.in_(["PENDIENTE", "PAGADA", "PAGADO"])
    ).all()
    citas_pendientes = [CitaPendiente(medico_id=c.medico_id, estado=c.estado) for c in citas_db]

    error = validar_restricciones_cita(cita_in.fecha_hora, cita_in.medico_id, citas_pendientes, ahora)
    if error:
        raise HTTPException(status_code=400, detail=error)

    jornada = db.query(Jornada).filter(
        Jornada.medico_id == cita_in.medico_id,
        Jornada.fecha_hora == cita_in.fecha_hora
    ).first()
    if not jornada:
        jornada = Jornada(medico_id=cita_in.medico_id, fecha_hora=cita_in.fecha_hora, duracion_minutos=60,
                          estado="DISPONIBLE")
        db.add(jornada)
        db.flush()

    error_jornada = validar_disponibilidad_jornada(
        SlotJornada(medico_id=jornada.medico_id, fecha_hora=jornada.fecha_hora, estado=jornada.estado))
    if error_jornada:
        raise HTTPException(status_code=400, detail=error_jornada)

    nueva_cita = Appointment(
        paciente_id=paciente_id,
        medico_id=cita_in.medico_id,
        fecha_hora=cita_in.fecha_hora,
        precio=500.00,
        estado="PENDIENTE",
        jornada_id=jornada.id
    )
    db.add(nueva_cita)
    db.flush()

    nueva_cita.folio_pago = generar_folio_pago(nueva_cita.id, nueva_cita.fecha_hora)
    jornada.estado = "PENDIENTE"

    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


@router.post("/citas/{cita_id}/pagar")
def simular_pago_cita(cita_id: int, payload: Optional[dict] = None, db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")

    if cita.estado == "CANCELADA":
        raise HTTPException(status_code=400, detail="No se puede pagar una cita que ya fue cancelada.")

    if cita.estado in ("PAGADA", "PAGADO"):
        return {"mensaje": "La cita ya se encuentra pagada.", "folio_pago": cita.folio_pago, "estado": cita.estado}

    folio_ingresado = payload.get("folio_pago") if payload else None
    if folio_ingresado:
        cita.folio_pago = folio_ingresado
    elif not cita.folio_pago:
        cita.folio_pago = generar_folio_pago(cita.id, cita.fecha_hora)

    cita.estado = "PAGADA"
    jornada = db.query(Jornada).filter(
        Jornada.medico_id == cita.medico_id,
        Jornada.fecha_hora == cita.fecha_hora
    ).first()
    if jornada:
        jornada.estado = "PAGADO"

    db.commit()
    db.refresh(cita)
    return {"mensaje": "Pago registrado con éxito.", "cita_id": cita.id, "folio_pago": cita.folio_pago,
            "estado": cita.estado}


@router.post("/citas/{cita_id}/cancelar")
def cancelar_cita_paciente(cita_id: int, usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cita_db = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita_db:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")
    if cita_db.estado == "CANCELADA":
        raise HTTPException(status_code=400, detail="Esta cita ya se encuentra cancelada.")

    momento_solicitud = datetime.now()
    es_valida, error_msg = es_cita_cancelable(cita_db.fecha_hora, momento_solicitud)
    if not es_valida:
        raise HTTPException(status_code=400, detail=error_msg)

    cita_cancelada, reembolso = procesar_cancelacion_cita(
        CitaInmutable(id=cita_db.id, fecha=cita_db.fecha_hora, precio=cita_db.precio, estado=cita_db.estado,
                     folio_pago=cita_db.folio_pago),
        momento_solicitud
    )
    cita_db.estado = cita_cancelada.estado

    jornada = db.query(Jornada).filter(
        Jornada.medico_id == cita_db.medico_id,
        Jornada.fecha_hora == cita_db.fecha_hora
    ).first()
    if jornada:
        jornada.estado = "DISPONIBLE"

    db.commit()
    return {"mensaje": "Cita cancelada con éxito.", "reembolso_calculado": reembolso}


@router.get("/citas")
def consultar_historial(usuario_actual: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paciente_id = usuario_actual.id
    resultados = db.query(Appointment, User).join(
        User, Appointment.medico_id == User.id
    ).filter(
        Appointment.paciente_id == paciente_id
    ).order_by(Appointment.fecha_hora.desc()).all()

    citas_detalladas = []
    for cita, medico in resultados:
        reembolso_texto = "N/A"
        if cita.estado == "CANCELADA":
            reembolso_texto = f"${cita.precio:.2f} (Reembolsado)"

        citas_detalladas.append({
            "id": cita.id,
            "paciente_id": cita.paciente_id,
            "medico_id": cita.medico_id,
            "fecha_hora": cita.fecha_hora,
            "precio": cita.precio,
            "estado": cita.estado,
            "folio_pago": cita.folio_pago,
            "reembolso": reembolso_texto,
            "medico_nombre": medico.nombre,
            "medico_especialidad": getattr(medico.perfil_medico, "especialidad", "Medicina General") if getattr(
                medico, "perfil_medico", None) else "Medicina General"
        })

    return citas_detalladas