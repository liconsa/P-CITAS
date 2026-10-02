from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.appointment import Appointment

router = APIRouter(prefix="/doctor", tags=["Médico"])


# ==========================================
# 1. VER CITAS ASIGNADAS AL MÉDICO
# ==========================================
@router.get("/{medico_id}/appointments")
def listar_mis_citas(medico_id: int, db: Session = Depends(get_db)):
    # Filtramos estrictamente por el ID del médico en sesión
    citas = db.query(Appointment).filter(Appointment.medico_id == medico_id).all()

    resultado = []
    for c in citas:
        # Buscamos los datos del paciente para mostrarlos en la tabla
        paciente = db.query(User).filter(User.id == c.paciente_id).first()

        resultado.append({
            "id": c.id,
            "paciente_nombre": paciente.nombre if paciente else f"Paciente #{c.paciente_id}",
            "fecha_hora": c.fecha_hora,
            "estado": c.estado
        })

    return resultado


# ==========================================
# 2. FINALIZAR / COMPLETAR CITA
# ==========================================
@router.post("/appointments/{cita_id}/complete")
def finalizar_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    # Cambiamos el estado para indicar que la consulta terminó
    cita.estado = "COMPLETADA"
    db.commit()

    return {"mensaje": "Consulta finalizada exitosamente"}