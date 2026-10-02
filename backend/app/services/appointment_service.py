from datetime import datetime, timedelta
from typing import Optional, List
from collections import namedtuple

# Estructura ligera para no acoplar la validación al modelo ORM (Paradigma funcional)
CitaPendiente = namedtuple("CitaPendiente", ["medico_id", "estado"])


def validar_restricciones_cita(fecha_solicitada: datetime, medico_id: int, citas_pendientes: List[CitaPendiente]) -> \
Optional[str]:
    ahora = datetime.now()

    # No se pueden solicitar citas correspondientes a fechas pasadas.[cite: 1]
    if fecha_solicitada < ahora:
        return "La fecha solicitada es en el pasado."

    # Una cita debe agendarse con un mínimo de 48 horas de anticipación.[cite: 1]
    if fecha_solicitada < (ahora + timedelta(hours=48)):
        return "La cita debe agendarse con un mínimo de 48 horas de anticipación."

    # Una cita debe agendarse con un máximo de tres meses.[cite: 1]
    if fecha_solicitada > (ahora + timedelta(days=90)):
        return "No se puede agendar con más de tres meses de anticipación."

    # Un paciente no puede agendar una nueva cita con el mismo médico si ya cuenta con una cita pendiente con ese médico.[cite: 1]
    for cita in citas_pendientes:
        if cita.medico_id == medico_id and cita.estado == "PENDIENTE":
            return "Ya cuentas con una cita pendiente con este médico."

    return None