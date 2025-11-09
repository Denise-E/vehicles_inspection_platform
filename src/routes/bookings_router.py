from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.booking_controller import (
    consultar_disponibilidad,
    reservar_turno,
    confirmar_turno,
    cancelar_turno,
    obtener_turno,
    listar_turnos_por_usuario,
    listar_turnos_por_vehiculo,
    listar_todos_los_turnos
)

bookings = Blueprint('bookings', __name__)


@bookings.route("/disponibilidad", methods=['POST'])
@token_required
def disponibilidad():
    """
    Consultar disponibilidad general del sistema
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            fecha_inicio:
              type: string
              format: date
              example: "2025-10-25"
              description: Fecha desde la cual buscar (opcional, por defecto hoy)
            fecha_final:
              type: string
              format: date
              example: "2025-11-10"
              description: Fecha hasta la cual buscar (opcional, si no se especifica muestra los próximos 15 días)
    responses:
      200:
        description: Slots disponibles del sistema (Lunes a Viernes, 9:00-20:00)
        schema:
          type: object
          properties:
            slots:
              type: array
              items:
                type: object
                properties:
                  fecha:
                    type: string
                    example: "2025-10-25 10:00"
                  disponible:
                    type: boolean
            total_disponibles:
              type: integer
              description: Cantidad total de slots disponibles
      400:
        description: Fecha inválida o rango de fechas incorrecto
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
    return consultar_disponibilidad()


@bookings.route("/reservar", methods=['POST'])
@token_required
def reservar():
    """
    Reservar un turno
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - matricula
            - fecha
            - creado_por
          properties:
            matricula:
              type: string
              example: ABC123
            fecha:
              type: string
              format: datetime
              example: "2025-10-25 10:00"
              description: Fecha y hora del turno (Lunes-Viernes 9-20hs)
            creado_por:
              type: integer
              example: 1
              description: ID del usuario que crea el turno
    responses:
      201:
        description: Turno reservado exitosamente (estado RESERVADO)
        schema:
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
              example: RESERVADO
            creado_por:
              type: integer
            nombre_creador:
              type: string
      400:
        description: Error en los datos, fecha inválida o turno ya existe
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
    return reservar_turno()


@bookings.route("/<int:turno_id>/confirmar", methods=['PUT'])
@token_required
def confirmar(turno_id: int):
    """
    Confirmar un turno
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: turno_id
        type: integer
        required: true
        description: ID del turno a confirmar
    responses:
      200:
        description: Turno confirmado exitosamente (estado CONFIRMADO)
        schema:
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
              example: CONFIRMADO
            creado_por:
              type: integer
            nombre_creador:
              type: string
      400:
        description: Turno no encontrado o no está en estado RESERVADO
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
    return confirmar_turno(turno_id)


@bookings.route("/<int:turno_id>/cancelar", methods=['PUT'])
@token_required
def cancelar(turno_id: int):
    """
    Cancelar un turno
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: turno_id
        type: integer
        required: true
        description: ID del turno a cancelar
    responses:
      200:
        description: Turno cancelado exitosamente (estado CANCELADO)
        schema:
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
              example: CANCELADO
            creado_por:
              type: integer
            nombre_creador:
              type: string
      400:
        description: Turno no encontrado o no puede ser cancelado
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
    return cancelar_turno(turno_id)


@bookings.route("/<int:turno_id>", methods=['GET'])
@token_required
def detalle(turno_id: int):
    """
    Obtener detalles de un turno
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: turno_id
        type: integer
        required: true
        description: ID del turno
    responses:
      200:
        description: Detalles del turno
        schema:
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
      400:
        description: Turno no encontrado
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
    return obtener_turno(turno_id)


@bookings.route("/usuario/<int:user_id>", methods=['GET'])
@token_required
def por_usuario(user_id: int):
    """
    Listar turnos de un usuario
    ---
    tags:
      - Turnos
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
        description: Lista de turnos creados por el usuario
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
    return listar_turnos_por_usuario(user_id)


@bookings.route("/vehiculo/<string:matricula>", methods=['GET'])
@token_required
def por_vehiculo(matricula: str):
    """
    Listar turnos de un vehículo
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: matricula
        type: string
        required: true
        description: Matrícula del vehículo
    responses:
      200:
        description: Lista de turnos del vehículo
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
      400:
        description: Vehículo no encontrado
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
    return listar_turnos_por_vehiculo(matricula)


@bookings.route("", methods=['GET'])
@token_required
def listar_todos():
    """
    Listar todos los turnos del sistema
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de todos los turnos del sistema (para administradores)
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
    return listar_todos_los_turnos()
