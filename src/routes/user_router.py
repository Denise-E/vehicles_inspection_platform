from flask import Blueprint

users = Blueprint('users', __name__)

# Users routes TODO: Define user model
@users.route("/register", methods=['POST']) 
# Register a new user
def register():
    return {"msg": 'User registered!'}, 200

@users.route("/login", methods=['POST'])
# Login a user
def login():
    return {"msg": 'User logged in!'}, 200
    
@users.route("/profile/<int:user_id>", methods=['GET'])
# Get user profile by id
def profile(user_id):
    return {"msg": 'User profile!'}, 200
