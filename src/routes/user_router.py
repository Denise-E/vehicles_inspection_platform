from flask import Blueprint

from src.controllers.user_controller import register_user, login_user

users = Blueprint('users', __name__)

@users.route("/register", methods=["POST"])
# Register a new user
def register():
    return register_user()

@users.route("/login", methods=['POST'])
# Login a user
def login():
    return login_user()
    
@users.route("/profile/<int:user_id>", methods=['GET'])
# Get user profile by id
def profile(user_id):
    return {"msg": 'User profile!'}, 200
