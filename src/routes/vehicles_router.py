from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.vehicles_controller import (
    register_vehicle,
    get_vehicle_profile,
    list_all_vehicles,
    update_vehicle,
    delete_vehicle
)

vehicles = Blueprint('vehicles', __name__)


@vehicles.route("/register/<int:duenio_id>", methods=['POST'])
@token_required
# Registrar un nuevo vehículo
def register(duenio_id: int):
    """
    Registra un nuevo vehículo. Requiere autenticación JWT.
    Request body: {"matricula": "ABC123", "marca": "Toyota", "modelo": "Corolla", "anio": 2020}
    Header: Authorization: Bearer <token>
    """
    return register_vehicle(duenio_id)


@vehicles.route("/profile/<string:matricula>", methods=['GET'])
@token_required
# Obtener perfil de un vehículo por matrícula
def profile(matricula: str):
    """
    Obtiene el perfil completo de un vehículo por su matrícula. Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return get_vehicle_profile(matricula)


@vehicles.route("", methods=['GET'])
@token_required
# Listar todos los vehículos
def listar():
    """
    Lista todos los vehículos del sistema. Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return list_all_vehicles()


@vehicles.route("/<string:matricula>", methods=['PUT'])
@token_required
# Actualizar un vehículo
def actualizar(matricula: str):
    """
    Actualiza los datos de un vehículo existente. Requiere autenticación JWT.
    Request body: {"marca": "Honda", "modelo": "Civic", "anio": 2021}
    Header: Authorization: Bearer <token>
    """
    return update_vehicle(matricula)


@vehicles.route("/<string:matricula>/desactivar", methods=['PATCH'])
@token_required
# Desactivar un vehículo (soft delete)
def desactivar(matricula: str):
    """
    Desactiva un vehículo (soft delete - cambia estado a INACTIVO). Requiere autenticación JWT.
    Más acorde a REST ya que modifica el estado del recurso sin eliminarlo.
    Header: Authorization: Bearer <token>
    """
    return delete_vehicle(matricula)

