from flask import Blueprint

bookings = Blueprint('bookings', __name__)

@bookings.route("/register", methods=['POST'])
# Register a new booking
def register_booking():
    return {"msg": 'Booking registered!'}, 200
    
@bookings.route("/profile/<int:booking_id>", methods=['GET'])
# Get booking details by id
def booking_details(booking_id):
    return {"msg": 'Booking profile!'}, 200
    
@bookings.route("/list", methods=['GET'])
# Get all bookings
def list_bookings():
    return {"msg": 'Bookings list!'}, 200
    
@bookings.route("/cancel/<int:booking_id>", methods=['PUT'])
# Cancel a booking
def cancel_booking(booking_id):
    return {"msg": 'Booking cancelled!'}, 200
    
@bookings.route("/list/<int:user_id>", methods=['GET'])
# Get all bookings by user id
def list_bookings_by_user(user_id):
    return {"msg": 'Bookings list by user!'}, 200
    
@bookings.route("/list/<string:matricula>", methods=['GET'])
# Get all bookings by vehicle matricula
def list_bookings_by_vehicle(matricula):
    return {"msg": 'Bookings list by vehicle!'}, 200

