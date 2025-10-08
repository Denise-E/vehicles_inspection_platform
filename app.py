from flask import Flask

app = Flask(__name__)

@app.route("/health", methods=['GET'])
def health():
    return {"msg": 'App running!'}, 200

# Users routes TODO: Define user model
@app.route("/users/register", methods=['POST']) 
# Register a new user
def register():
    return {"msg": 'User registered!'}, 200

@app.route("/users/login", methods=['POST'])
# Login a user
def login():
    return {"msg": 'User logged in!'}, 200
    
@app.route("/users/profile/<int:user_id>", methods=['GET'])
# Get user profile by id
def profile(user_id):
    return {"msg": 'User profile!'}, 200

# Vehicles routes TODO: Define vehicle model
@app.route("/vehicles/register", methods=['POST'])
# Register a new vehicle
def register_vehicle():
    return {"msg": 'Vehicle registered!'}, 200
    
@app.route("/vehicles/profile/<string:matricula>", methods=['GET'])
# Get vehicle profile by id
def profile_vehicle(matricula):
    return {"msg": 'Vehicle profile!'}, 200
    
@app.route("/vehicles/list", methods=['GET'])
# Get all vehicles
def list_vehicles():
    return {"msg": 'Vehicles list!'}, 200


# Bookings routes TODO: Define booking model
@app.route("/bookings/register", methods=['POST'])
# Register a new booking
def register_booking():
    return {"msg": 'Booking registered!'}, 200
    
@app.route("/bookings/profile/<int:booking_id>", methods=['GET'])
# Get booking details by id
def booking_details(booking_id):
    return {"msg": 'Booking profile!'}, 200
    
@app.route("/bookings/list", methods=['GET'])
# Get all bookings
def list_bookings():
    return {"msg": 'Bookings list!'}, 200
    
@app.route("/bookings/cancel/<int:booking_id>", methods=['PUT'])
# Cancel a booking
def cancel_booking(booking_id):
    return {"msg": 'Booking cancelled!'}, 200
    
@app.route("/bookings/list/<int:user_id>", methods=['GET'])
# Get all bookings by user id
def list_bookings_by_user(user_id):
    return {"msg": 'Bookings list by user!'}, 200
    
@app.route("/bookings/list/<string:matricula>", methods=['GET'])
# Get all bookings by vehicle matricula
def list_bookings_by_vehicle(matricula):
    return {"msg": 'Bookings list by vehicle!'}, 200


# Inspections routes TODO: Define inspection model
@app.route("/inspections/register", methods=['POST'])
# Register a new inspection
def register_inspection():
    return {"msg": 'Inspection registered!'}, 200
    
@app.route("/inspections/profile/<int:inspection_id>", methods=['GET'])
# Get inspection details by id
def inspection_details(inspection_id):
    return {"msg": 'Inspection profile!'}, 200
    


if __name__ == "__main__":
    app.run(debug=True)