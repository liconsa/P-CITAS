from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from app.core.database import get_db

from app.models.appointment import Appointment
# Importamos el modelo User para poder buscar a los médicos
from app.models.user import User

from app.schemas.appointment_schema import AppointmentCreate, AppointmentResponse
from app.services.appointment_service import validar_restricciones_cita, CitaPendiente
from app.services.cancellation_policies import procesar_cancelacion_cita, CitaInmutable

# El prefijo /patient se aplica a TODAS las rutas de este archivo
router = APIRouter(prefix="/patient", tags=["Paciente"])


# ==========================================
# RUTAS NUEVAS PARA EL FRONTEND (CALENDARIO)
# ==========================================

@router.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    # Busca usuarios cuyo rol sea MEDICO
    doctores = db.query(User).filter(User.rol == 'MEDICO').all()
    # Si no tienes columna especialidad, devuelve un texto por defecto
    return [{"id": d.id, "nombre": d.nombre, "especialidad": getattr(d, "especialidad", "Medicina General")} for d in
            doctores]


@router.get("/doctor/{doctor_id}/occupied-days")
def get_occupied_days(doctor_id: int, year: int, month: int, db: Session = Depends(get_db)):
    citas = db.query(Appointment).filter(
        Appointment.medico_id == doctor_id,
        extract('year', Appointment.fecha_hora) == year,
        extract('month', Appointment.fecha_hora) == month
    ).all()

    conteo_por_dia = {}
    for cita in citas:
        dia = cita.fecha_hora.day
        conteo_por_dia[dia] = conteo_por_dia.get(dia, 0) + 1

    MAX_CITAS_DIA = 6  # Límite de citas por día
    dias_ocupados = [dia for dia, conteo in conteo_por_dia.items() if conteo >= MAX_CITAS_DIA]
    return {"dias_ocupados": dias_ocupados}


@router.get("/doctor/{doctor_id}/available-hours")
def get_available_hours(doctor_id: int, date: str, db: Session = Depends(get_db)):
    fecha_obj = datetime.strptime(date, "%Y-%m-%d").date()
    horarios_base = ["09:00", "10:30", "12:00", "13:30", "15:00", "16:30"]

    citas_del_dia = db.query(Appointment).filter(
        Appointment.medico_id == doctor_id,
        extract('year', Appointment.fecha_hora) == fecha_obj.year,
        extract('month', Appointment.fecha_hora) == fecha_obj.month,
        extract('day', Appointment.fecha_hora) == fecha_obj.day
    ).all()

    horas_ocupadas = [cita.fecha_hora.strftime("%H:%M") for cita in citas_del_dia]
    horas_disponibles = [h for h in horarios_base if h not in horas_ocupadas]
    return {"horas": horas_disponibles}


# ==========================================
# TUS RUTAS ORIGINALES INTACTAS
# ==========================================

@router.post("/citas", response_model=AppointmentResponse)
def agendar_cita(cita_in: AppointmentCreate, paciente_id: int = 1, db: Session = Depends(get_db)):
    # Obtener citas pendientes del paciente para la validación
    citas_db = db.query(Appointment).filter(
        Appointment.paciente_id == paciente_id,
        Appointment.estado == "PENDIENTE"
    ).all()

    # Transformar a estructura inmutable para la función pura
    citas_pendientes = [CitaPendiente(medico_id=c.medico_id, estado=c.estado) for c in citas_db]

    # Validar reglas de negocio: antelación, límites temporales y citas previas
    error = validar_restricciones_cita(cita_in.fecha_hora, cita_in.medico_id, citas_pendientes)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Efecto secundario: Guardar en BD si las validaciones puras pasaron
    nueva_cita = Appointment(
        paciente_id=paciente_id,
        medico_id=cita_in.medico_id,
        fecha_hora=cita_in.fecha_hora,
        precio=500.00  # Precio base simulado
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

    # Convertir a estructura inmutable para la lógica funcional
    cita_inmutable = CitaInmutable(
        id=cita_db.id,
        fecha=cita_db.fecha_hora,
        precio=cita_db.precio,
        estado=cita_db.estado
    )

    # Procesar cancelación mediante composición de funciones puras
    cita_cancelada, reembolso = procesar_cancelacion_cita(cita_inmutable, datetime.now())

    # Efecto secundario: Actualizar base de datos
    cita_db.estado = cita_cancelada.estado
    db.commit()

    return {
        "mensaje": "Cita cancelada exitosamente",
        "estado": cita_cancelada.estado,
        "reembolso_calculado": reembolso
    }


@router.get("/citas")
def consultar_historial(paciente_id: int = 1, db: Session = Depends(get_db)):
    # Hacemos un JOIN con la tabla User para traer el nombre y la especialidad del médico
    resultados = db.query(Appointment, User).join(
        User, Appointment.medico_id == User.id
    ).filter(Appointment.paciente_id == paciente_id).all()

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