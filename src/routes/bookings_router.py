from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.booking_controller import (
    consultar_disponibilidad,
    reservar_turno,
    actualizar_turno,
    obtener_turno,
    listar_todos_los_turnos
)

bookings = Blueprint('bookings', __name__)


@bookings.route("/availability", methods=['POST'])
@token_required
def availability():
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


@bookings.route("", methods=['POST'])
@token_required
def crear():
    """
    Crear un turno
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
          properties:
            matricula:
              type: string
              example: ABC123
            fecha:
              type: string
              format: datetime
              example: "2025-10-25 10:00"
              description: Fecha y hora del turno (Lunes-Viernes 9-20hs)
    responses:
      201:
        description: Turno creado exitosamente (estado RESERVADO)
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
              description: ID del usuario que creó el turno (obtenido del token JWT)
            nombre_creador:
              type: string
      400:
        description: Error - vehículo no encontrado, INACTIVO, no es propietario, fecha inválida o turno ya existe
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No se puede crear un turno para un vehículo INACTIVO"
      401:
        description: Token no proporcionado o inválido
        schema:
          type: object
          properties:
            error:
              type: string
      403:
        description: Sin permisos (si intenta crear turno para vehículo que no le pertenece)
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return reservar_turno()


@bookings.route("/<int:turno_id>", methods=['PUT'])
@token_required
def actualizar(turno_id: int):
    """
    Actualizar el estado de un turno
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
        description: ID del turno a actualizar
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - estado_id
          properties:
            estado_id:
              type: integer
              example: 2
              description: |
                ID del nuevo estado:
                - 1: RESERVADO
                - 2: CONFIRMADO
                - 3: COMPLETADO
                - 4: CANCELADO
                
                Transiciones válidas:
                - RESERVADO → CONFIRMADO o CANCELADO
                - CONFIRMADO → COMPLETADO o CANCELADO
    responses:
      200:
        description: Estado del turno actualizado exitosamente
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
        description: Turno no encontrado, en estado final, transición no permitida o sin permisos
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No tienes permiso para modificar este turno. Solo puedes modificar turnos de tus propios vehículos"
      401:
        description: Token no proporcionado o inválido
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return actualizar_turno(turno_id)


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
            puntuacion_total:
              type: integer
              description: Puntuación de la inspección (solo para turnos COMPLETADO)
            resultado:
              type: string
              description: Resultado de la inspección (solo para turnos COMPLETADO)
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

@bookings.route("", methods=['GET'])
@token_required
def listar_todos():
    """
    Listar turnos del sistema
    ---
    tags:
      - Turnos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de turnos según permisos del usuario
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
                  puntuacion_total:
                    type: integer
                    description: Puntuación de la inspección (solo para turnos COMPLETADO)
                  resultado:
                    type: string
                    description: Resultado de la inspección (solo para turnos COMPLETADO)
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
