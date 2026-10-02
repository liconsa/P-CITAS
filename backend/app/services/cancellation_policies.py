from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple

# 1. INMUTABILIDAD: Usamos dataclasses con frozen=True.
# Esto significa que una vez creada la CitaInmutable, es imposible alterarla.
@dataclass(frozen=True)
class CitaInmutable:
    id: int
    fecha: datetime
    precio: float
    estado: str

# 2. FUNCIÓN PURA: Calcula el porcentaje según el Requerimiento 7
def calcular_porcentaje_reembolso(fecha_cita: datetime, fecha_cancelacion: datetime) -> float:
    """
    Función pura que evalúa el requerimiento 7 sin alterar el entorno.
    """
    tiempo_restante = fecha_cita - fecha_cancelacion

    if tiempo_restante < timedelta(hours=24):
        return 0.0  # 0% de devolución
    elif timedelta(hours=24) <= tiempo_restante < timedelta(hours=48):
        return 0.5  # 50% de devolución
    else:
        return 1.0  # 100% de devolución

# 3. COMPOSICIÓN DE FUNCIONES: Procesamos la cancelación creando nuevos estados
def procesar_cancelacion_cita(cita: CitaInmutable, fecha_cancelacion: datetime) -> Tuple[CitaInmutable, float]:
    """
    Función pura. Recibe el estado actual (inmutable) y retorna el nuevo estado
    y el cálculo financiero, sin modificar la base de datos ni la cita original.
    """
    # Calculamos el dinero llamando a otra función pura
    porcentaje = calcular_porcentaje_reembolso(cita.fecha, fecha_cancelacion)
    reembolso_total = cita.precio * porcentaje

    # Requerimiento 5: No se reagenda, se cancela.
    # En lugar de hacer cita.estado = "CANCELADA" (lo cual violaría el paradigma funcional),
    # retornamos una NUEVA instancia con el estado actualizado.
    cita_cancelada = CitaInmutable(
        id=cita.id,
        fecha=cita.fecha,
        precio=cita.precio,
        estado="CANCELADA"
    )

    return cita_cancelada, reembolso_total