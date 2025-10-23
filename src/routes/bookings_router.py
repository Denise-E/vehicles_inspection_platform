from flask import Blueprint
from src.utils.jwt_utils import token_required
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
@token_required
# Consultar disponibilidad de turnos para un vehículo
def disponibilidad():
    """
    Consulta los slots disponibles para un vehículo. Requiere autenticación JWT.
    Request body: {"matricula": "ABC123", "fecha_inicio": "2025-10-25"} (fecha_inicio es opcional)
    Header: Authorization: Bearer <token>
    """
    return consultar_disponibilidad()


@bookings.route("/reservar", methods=['POST'])
@token_required
# Reservar un turno
def reservar():
    """
    Crea un nuevo turno en estado RESERVADO. Requiere autenticación JWT.
    Request body: {"matricula": "ABC123", "fecha": "2025-10-25 10:00", "creado_por": 1}
    Header: Authorization: Bearer <token>
    """
    return reservar_turno()


@bookings.route("/<int:turno_id>/confirmar", methods=['PUT'])
@token_required
# Confirmar un turno
def confirmar(turno_id: int):
    """
    Confirma un turno (cambia estado a CONFIRMADO). Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return confirmar_turno(turno_id)


@bookings.route("/<int:turno_id>/cancelar", methods=['PUT'])
@token_required
# Cancelar un turno
def cancelar(turno_id: int):
    """
    Cancela un turno (cambia estado a CANCELADO). Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return cancelar_turno(turno_id)


@bookings.route("/<int:turno_id>", methods=['GET'])
@token_required
# Obtener detalles de un turno por ID
def detalle(turno_id: int):
    """
    Obtiene los detalles de un turno específico. Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return obtener_turno(turno_id)


@bookings.route("/usuario/<int:user_id>", methods=['GET'])
@token_required
# Listar turnos de un usuario
def por_usuario(user_id: int):
    """
    Lista todos los turnos creados por un usuario específico. Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return listar_turnos_por_usuario(user_id)


@bookings.route("/vehiculo/<string:matricula>", methods=['GET'])
@token_required
# Listar turnos de un vehículo
def por_vehiculo(matricula: str):
    """
    Lista todos los turnos de un vehículo específico. Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return listar_turnos_por_vehiculo(matricula)


@bookings.route("", methods=['GET'])
@token_required
# Listar todos los turnos
def listar_todos():
    """
    Lista todos los turnos del sistema (para vista admin). Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return listar_todos_los_turnos()

