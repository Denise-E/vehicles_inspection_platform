from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.user_controller import register_user, login_user, get_user_profile
from src.controllers.booking_controller import listar_turnos_por_usuario
from src.controllers.inspection_controller import list_inspections_by_inspector

users = Blueprint('users', __name__)

@users.route("", methods=["POST"])
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

@users.route("/sessions", methods=['POST'])
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
    
@users.route("/<int:user_id>", methods=['GET'])
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


@users.route("/bookings", methods=['GET'])
@token_required
def user_bookings():
    """
    Listar turnos del usuario autenticado
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de turnos del usuario autenticado (obtenido del token JWT)
        schema:
          type: object
          properties:
            turnos:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  vehiculo_id:
                    type: integer
                  matricula:
                    type: string
                  fecha:
                    type: string
                  estado:
                    type: string
                  creado_por:
                    type: integer
                  nombre_creador:
                    type: string
            total:
              type: integer
      401:
        description: Token no proporcionado o inválido
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return listar_turnos_por_usuario()


@users.route("/<int:inspector_id>/inspections", methods=['GET'])
@token_required
def inspector_inspections(inspector_id: int):
    """
    Listar inspecciones de un inspector
    
    Autorización:
    - ADMIN: puede ver inspecciones de cualquier inspector
    - INSPECTOR: solo puede ver sus propias inspecciones
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: inspector_id
        type: integer
        required: true
        description: ID del inspector
    responses:
      200:
        description: Lista de inspecciones del inspector
        schema:
          type: object
          properties:
            inspecciones:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  turno_id:
                    type: integer
                  vehiculo_matricula:
                    type: string
                  inspector_nombre:
                    type: string
                  fecha:
                    type: string
                    format: date-time
                  puntuacion_total:
                    type: integer
                  resultado:
                    type: string
                  observacion:
                    type: string
                  estado:
                    type: string
            total:
              type: integer
      400:
        description: Inspector no encontrado
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
    return list_inspections_by_inspector(inspector_id)
