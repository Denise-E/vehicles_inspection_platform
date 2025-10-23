from flask import Blueprint
from src.controllers.vehicles_controller import (
    register_vehicle,
    get_vehicle_profile,
    list_all_vehicles,
    update_vehicle,
    delete_vehicle
)

vehicles = Blueprint('vehicles', __name__)


@vehicles.route("/register/<int:duenio_id>", methods=['POST'])
# Registrar un nuevo vehículo
def register(duenio_id: int):
    """
    Registra un nuevo vehículo.
    Request body: {"matricula": "ABC123", "marca": "Toyota", "modelo": "Corolla", "anio": 2020}
    TODO: Manejar duenio_id con token JWT cuando se implemente autenticación
    """
    return register_vehicle(duenio_id)


@vehicles.route("/profile/<string:matricula>", methods=['GET'])
# Obtener perfil de un vehículo por matrícula
def profile(matricula: str):
    """
    Obtiene el perfil completo de un vehículo por su matrícula.
    """
    return get_vehicle_profile(matricula)


@vehicles.route("", methods=['GET'])
# Listar todos los vehículos
def listar():
    """
    Lista todos los vehículos del sistema.
    """
    return list_all_vehicles()


@vehicles.route("/<string:matricula>", methods=['PUT'])
# Actualizar un vehículo
def actualizar(matricula: str):
    """
    Actualiza los datos de un vehículo existente.
    Request body: {"marca": "Honda", "modelo": "Civic", "anio": 2021}
    """
    return update_vehicle(matricula)


@vehicles.route("/<string:matricula>/desactivar", methods=['PATCH'])
# Desactivar un vehículo (soft delete)
def desactivar(matricula: str):
    """
    Desactiva un vehículo (soft delete - cambia estado a INACTIVO).
    Más acorde a REST ya que modifica el estado del recurso sin eliminarlo.
    """
    return delete_vehicle(matricula)

