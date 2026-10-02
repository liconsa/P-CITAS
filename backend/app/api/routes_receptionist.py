from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, RolUsuario
from app.models.appointment import Appointment

router = APIRouter(prefix="/receptionist", tags=["Recepcionista"])


@router.put("/doctores/{doctor_id}/estado")
def gestionar_estado_medico(doctor_id: int, activo: bool, db: Session = Depends(get_db)):
    # El recepcionista podrá realizar operaciones de alta y baja del personal médico.[cite: 1]
    doctor = db.query(User).filter(User.id == doctor_id, User.rol == RolUsuario.MEDICO).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    doctor.activo = activo
    db.commit()
    estado_str = "alta" if activo else "baja"
    return {"mensaje": f"Médico dado de {estado_str} exitosamente."}


@router.put("/citas/{cita_id}/estado")
def gestionar_estado_cita(cita_id: int, nuevo_estado: str, db: Session = Depends(get_db)):
    # El recepcionista podrá intervenir en el proceso de confirmación o cancelación de citas.[cite: 1]
    estados_validos = ["CONFIRMADA", "CANCELADA", "PENDIENTE"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado no válido")

    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = nuevo_estado
    db.commit()
    return {"mensaje": f"Estado de la cita actualizado a {nuevo_estado}."}