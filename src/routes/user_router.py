from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.user_controller import register_user, login_user, get_user_profile

users = Blueprint('users', __name__)

@users.route("/register", methods=["POST"])
def register():
    """
    Registrar un nuevo usuario
    ---
    tags:
      - Usuarios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre_completo
            - mail
            - contrasenia
            - rol
          properties:
            nombre_completo:
              type: string
              example: Juan Perez
              minLength: 3
            mail:
              type: string
              format: email
              example: juan@example.com
            telefono:
              type: string
              example: "123456789"
              minLength: 6
              maxLength: 20
            contrasenia:
              type: string
              format: password
              example: password123
              minLength: 6
            rol:
              type: string
              enum: [DUENIO, INSPECTOR, ADMIN]
              example: DUENIO
    responses:
      201:
        description: Usuario registrado exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
            nombre_completo:
              type: string
            mail:
              type: string
            telefono:
              type: string
            rol:
              type: string
            activo:
              type: boolean
      400:
        description: Error en los datos proporcionados
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return register_user()

@users.route("/login", methods=['POST'])
def login():
    """
    Iniciar sesión y obtener token JWT
    ---
    tags:
      - Usuarios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - mail
            - contrasenia
          properties:
            mail:
              type: string
              format: email
              example: juan@example.com
            contrasenia:
              type: string
              format: password
              example: password123
    responses:
      200:
        description: Login exitoso, retorna token JWT
        schema:
          type: object
          properties:
            id:
              type: integer
            nombre_completo:
              type: string
            mail:
              type: string
            telefono:
              type: string
            rol:
              type: string
            activo:
              type: boolean
            token:
              type: string
              description: JWT Bearer token válido por 24 horas
      400:
        description: Credenciales inválidas
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return login_user()
    
@users.route("/profile/<int:user_id>", methods=['GET'])
@token_required
def profile(user_id):
    """
    Obtener perfil de usuario por ID
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID del usuario
    responses:
      200:
        description: Perfil del usuario
        schema:
          type: object
          properties:
            id:
              type: integer
            nombre_completo:
              type: string
            mail:
              type: string
            telefono:
              type: string
            rol:
              type: string
            activo:
              type: boolean
      400:
        description: Usuario no encontrado
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Token no proporcionado o inválido
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return get_user_profile(user_id)
