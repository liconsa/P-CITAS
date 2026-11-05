from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.appointment import Appointment
from app.api.routes_auth import get_current_user

router = APIRouter(prefix="/doctor", tags=["Médico"])

# Simulación temporal de códigos de verificación enviados a pacientes
CODIGOS_PACIENTES = {}


@router.get("/{doctor_id}/appointments")
def listar_citas_doctor(doctor_id: int, db: Session = Depends(get_db)):
    citas = db.query(Appointment).filter(Appointment.medico_id == doctor_id).all()
    resultado = []
    for c in citas:
        paciente = db.query(User).filter(User.id == c.paciente_id).first()
        resultado.append({
            "id": c.id,
            "paciente_id": c.paciente_id,
            "paciente_nombre": paciente.nombre if paciente else "Paciente Desconocido",
            "fecha_hora": c.fecha_hora,
            "precio": c.precio,
            "estado": c.estado,
            "folio_pago": c.folio_pago
        })
    return resultado


@router.post("/appointments/{cita_id}/send-code")
def enviar_codigo_paciente(cita_id: int, usuario_actual: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")

    # Generamos un código aleatorio de 4 dígitos
    import random
    codigo_generado = str(random.randint(1000, 9999))
    CODIGOS_PACIENTES[cita_id] = codigo_generado

    # IMPRESIÓN CLARA Y VISIBLE EN LA CONSOLA DE PYTHON (TERMINAL)
    print("\n" + "="*50)
    print(f" 🔑 [CÓDIGO DE VERIFICACIÓN] Cita #{cita_id}")
    print(f" 📲 Enviado al paciente -> CLAVE: {codigo_generado}")
    print("="*50 + "\n")

    return {
        "mensaje": f"Código de verificación enviado al paciente. (Clave generada: {codigo_generado})",
        "codigo_simulado": codigo_generado # Para que aparezca en el alert y sea rapidísimo probarlo
    }


@router.post("/appointments/{cita_id}/verify-and-complete")
def verificar_codigo_y_completar(cita_id: int, payload: dict, usuario_actual: User = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    cita = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")

    if cita.medico_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No autorizado.")

    codigo_ingresado = payload.get("codigo")
    codigo_correcto = CODIGOS_PACIENTES.get(cita_id)

    if not codigo_correcto or codigo_ingresado != codigo_correcto:
        raise HTTPException(status_code=400, detail="Código de verificación incorrecto o expirado.")

    cita.estado = "COMPLETADA"
    db.commit()

    # Limpiamos el código usado
    CODIGOS_PACIENTES.pop(cita_id, None)

    return {"mensaje": "Consulta finalizada exitosamente mediante código del paciente."}