from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple, Optional
import uuid

# ==============================================================================
# PARADIGMA FUNCIONAL: INMUTABILIDAD Y ESTRUCTURAS DE DATOS PURAS
# ==============================================================================

@dataclass(frozen=True)
class CitaInmutable:
    id: int
    fecha: datetime
    precio: float
    estado: str
    folio_pago: Optional[str] = None

# 1. FUNCIÓN PURA: Validación de cancelación temporal
def es_cita_cancelable(fecha_cita: datetime, fecha_cancelacion: datetime) -> Tuple[bool, Optional[str]]:
    """
    Función pura que valida si la cita es temporalmente cancelable.
    No se puede cancelar una cita cuya hora ya transcurrió.
    """
    if fecha_cita <= fecha_cancelacion:
        return False, "No se puede cancelar una cita que ya ha transcurrido o iniciado."
    return True, None

# 2. FUNCIÓN PURA: Calcula el porcentaje según el Requerimiento de cancelación
def calcular_porcentaje_reembolso(fecha_cita: datetime, fecha_cancelacion: datetime) -> float:
    """
    Función pura que evalúa la política de reembolso sin alterar el entorno:
    - Menos de 24 horas: 0% de devolución.
    - Entre 24 y 48 horas: 50% de devolución.
    - 48 horas o más: 100% de devolución.
    """
    tiempo_restante = fecha_cita - fecha_cancelacion

    if tiempo_restante < timedelta(hours=24):
        return 0.0  # 0% de devolución
    elif timedelta(hours=24) <= tiempo_restante < timedelta(hours=48):
        return 0.5  # 50% de devolución
    else:
        return 1.0  # 100% de devolución

# 3. COMPOSICIÓN DE FUNCIONES: Procesamiento de cancelación inmutable
def procesar_cancelacion_cita(cita: CitaInmutable, fecha_cancelacion: datetime) -> Tuple[CitaInmutable, float]:
    """
    Función pura. Recibe el estado actual (inmutable) y retorna el nuevo estado
    y el cálculo financiero, sin modificar la base de datos ni la cita original.
    """
    porcentaje = calcular_porcentaje_reembolso(cita.fecha, fecha_cancelacion)
    reembolso_total = round(cita.precio * porcentaje, 2)

    # Retornamos una NUEVA instancia con el estado inmutable actualizado a CANCELADA
    cita_cancelada = CitaInmutable(
        id=cita.id,
        fecha=cita.fecha,
        precio=cita.precio,
        estado="CANCELADA",
        folio_pago=cita.folio_pago
    )

    return cita_cancelada, reembolso_total

# 4. FUNCIÓN PURA: Generador determinista de folio de pago
def generar_folio_pago(cita_id: int, fecha_hora: datetime) -> str:
    """
    Genera un folio de pago simulado con formato identificador único.
    """
    prefijo = fecha_hora.strftime("%Y%m%d")
    sufijo_uuid = uuid.uuid4().hex[:6].upper()
    return f"FOL-{prefijo}-{cita_id:04d}-{sufijo_uuid}"
