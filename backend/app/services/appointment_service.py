from datetime import datetime, timedelta
from typing import Optional, List
from collections import namedtuple

# ==============================================================================
# PARADIGMA FUNCIONAL: VALIDACIONES PURAS DE REGLAS DE NEGOCIO
# ==============================================================================

# Estructura inmutable ligera para desacoplar validaciones de SQLAlchemy
CitaPendiente = namedtuple("CitaPendiente", ["medico_id", "estado"])
SlotJornada = namedtuple("SlotJornada", ["medico_id", "fecha_hora", "estado"])


def validar_restricciones_cita(
    fecha_solicitada: datetime,
    medico_id: int,
    citas_pendientes: List[CitaPendiente],
    ahora: Optional[datetime] = None
) -> Optional[str]:
    """
    Función pura que valida todas las restricciones temporales y de estado:
    1. No se pueden solicitar citas en fechas pasadas.
    2. Debe agendarse con mínimo 48 horas de anticipación.
    3. No se puede agendar con más de 3 meses (90 días) de anticipación.
    4. Un paciente no puede agendar si ya tiene cita PENDIENTE o PAGADA con el mismo médico.
    """
    if ahora is None:
        ahora = datetime.now()

    # 1. Validación de fecha en el pasado
    if fecha_solicitada < ahora:
        return "La fecha solicitada es en el pasado."

    # 2. Anticipación mínima de 48 horas
    if fecha_solicitada < (ahora + timedelta(hours=48)):
        return "La cita debe agendarse con un mínimo de 48 horas de anticipación."

    # 3. Anticipación máxima de 3 meses (90 días)
    if fecha_solicitada > (ahora + timedelta(days=90)):
        return "No se puede agendar una cita con más de tres meses (90 días) de anticipación."

    # 4. No duplicar cita activa con el mismo médico
    for cita in citas_pendientes:
        if cita.medico_id == medico_id and cita.estado in ("PENDIENTE", "PAGADA", "PAGADO"):
            return "Ya cuentas con una cita pendiente o pagada con este médico."

    return None


def validar_disponibilidad_jornada(slot: Optional[SlotJornada]) -> Optional[str]:
    """
    Valida si la jornada asignada por el administrador está abierta para reserva.
    """
    if slot is None:
        return "El médico no tiene jornada laboral asignada en este horario."

    if slot.estado != "DISPONIBLE":
        return f"El horario seleccionado ya no está disponible (estado actual: {slot.estado})."

    return None
