from flask import Blueprint
from src.controllers.booking_controller import (
    consultar_disponibilidad,
    reservar_turno,
    confirmar_turno,
    cancelar_turno,
    obtener_turno,
    listar_turnos_por_usuario,
    listar_turnos_por_vehiculo,
    listar_todos_los_turnos
)

bookings = Blueprint('bookings', __name__)


@bookings.route("/disponibilidad", methods=['POST'])
# Consultar disponibilidad de turnos para un vehículo
def disponibilidad():
    """
    Consulta los slots disponibles para un vehículo.
    Request body: {"matricula": "ABC123", "fecha_inicio": "2025-10-25"} (fecha_inicio es opcional)
    """
    return consultar_disponibilidad()


@bookings.route("/reservar", methods=['POST'])
# Reservar un turno
def reservar():
    """
    Crea un nuevo turno en estado RESERVADO.
    Request body: {"matricula": "ABC123", "fecha": "2025-10-25 10:00", "creado_por": 1}
    """
    return reservar_turno()


@bookings.route("/<int:turno_id>/confirmar", methods=['PUT'])
# Confirmar un turno
def confirmar(turno_id: int):
    """
    Confirma un turno (cambia estado a CONFIRMADO).
    """
    return confirmar_turno(turno_id)


@bookings.route("/<int:turno_id>/cancelar", methods=['PUT'])
# Cancelar un turno
def cancelar(turno_id: int):
    """
    Cancela un turno (cambia estado a CANCELADO).
    """
    return cancelar_turno(turno_id)


@bookings.route("/<int:turno_id>", methods=['GET'])
# Obtener detalles de un turno por ID
def detalle(turno_id: int):
    """
    Obtiene los detalles de un turno específico.
    """
    return obtener_turno(turno_id)


@bookings.route("/usuario/<int:user_id>", methods=['GET'])
# Listar turnos de un usuario
def por_usuario(user_id: int):
    """
    Lista todos los turnos creados por un usuario específico.
    """
    return listar_turnos_por_usuario(user_id)


@bookings.route("/vehiculo/<string:matricula>", methods=['GET'])
# Listar turnos de un vehículo
def por_vehiculo(matricula: str):
    """
    Lista todos los turnos de un vehículo específico.
    """
    return listar_turnos_por_vehiculo(matricula)


@bookings.route("", methods=['GET'])
# Listar todos los turnos
def listar_todos():
    """
    Lista todos los turnos del sistema (para vista admin).
    """
    return listar_todos_los_turnos()

