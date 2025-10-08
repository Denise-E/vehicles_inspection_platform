from flask import Blueprint

vehicles = Blueprint('vehicles', __name__)


@vehicles.route("/register", methods=['POST'])
# Register a new vehicle
def register_vehicle():
    return {"msg": 'Vehicle registered!'}, 200
    
@vehicles.route("/profile/<string:matricula>", methods=['GET'])
# Get vehicle profile by id
def profile_vehicle(matricula):
    return {"msg": 'Vehicle profile!'}, 200
    
@vehicles.route("/list", methods=['GET'])
# Get all vehicles
def list_vehicles():
    return {"msg": 'Vehicles list!'}, 200

