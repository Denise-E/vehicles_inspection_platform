from flask import Blueprint
from src.controllers.vehicles_controller import register_vehicle

vehicles = Blueprint('vehicles', __name__)


@vehicles.route("/register/<int:duenio_id>", methods=['POST'])
# Register a new vehicle
def register(duenio_id): # TODO manejarlo con token
    return register_vehicle(duenio_id)
    
@vehicles.route("/profile/<string:matricula>", methods=['GET'])
# Get vehicle profile by id
def profile(matricula):
    return {"msg": 'Vehicle profile!'}, 200
    
@vehicles.route("/list", methods=['GET'])
# Get all vehicles
def list():
    return {"msg": 'Vehicles list!'}, 200

