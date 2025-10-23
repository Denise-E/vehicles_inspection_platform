from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.user_controller import register_user, login_user, get_user_profile

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
@token_required
# Get user profile by id
def profile(user_id):
    """
    Obtiene el perfil de un usuario. Requiere autenticación JWT.
    Header: Authorization: Bearer <token>
    """
    return get_user_profile(user_id)
