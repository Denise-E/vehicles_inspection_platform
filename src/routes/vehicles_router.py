from flask import Blueprint
from src.controllers.vehicles_controller import (
    register_vehicle,
    get_vehicle_profile,
    list_all_vehicles
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

