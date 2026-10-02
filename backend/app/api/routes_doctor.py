from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.appointment import Appointment

router = APIRouter(prefix="/doctor", tags=["Médico"])

@router.get("/agenda")
def consultar_agenda(medico_id: int = 2, db: Session = Depends(get_db)): # medico_id provendría del token JWT
    # El médico podrá visualizar sus citas programadas.[cite: 1]
    citas = db.query(Appointment).filter(
        Appointment.medico_id == medico_id,
        Appointment.estado == "PENDIENTE"
    ).order_by(Appointment.fecha_hora).all()
    return citas

@router.get("/pacientes/{paciente_id}/historial")
def consultar_historial_medico(paciente_id: int, db: Session = Depends(get_db)):
    # El médico podrá consultar el historial médico correspondiente a sus pacientes.[cite: 1]
    historial = db.query(Appointment).filter(Appointment.paciente_id == paciente_id).all()
    return {"paciente_id": paciente_id, "historial": historial}

# Aquí se integraría la ruta para generar recetas:
# El médico podrá generar recetas relacionadas con los pacientes atendidos.[cite: 1]
@router.post("/recetas")
def registrar_receta_medica():
    # La implementación utilizaría un esquema funcional para procesar medicamentos
    # como se define en el paradigma funcional mediante MAP.[cite: 1]
    return {"mensaje": "Receta generada en desarrollo."}