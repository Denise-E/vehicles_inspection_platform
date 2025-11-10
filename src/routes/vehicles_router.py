from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.vehicles_controller import (
    register_vehicle,
    get_vehicle_profile,
    list_all_vehicles,
    update_vehicle,
    delete_vehicle
)
from src.controllers.booking_controller import listar_turnos_por_vehiculo
from src.controllers.inspection_controller import list_inspections_by_vehiculo

vehicles = Blueprint('vehicles', __name__)


@vehicles.route("", methods=['POST'])
@token_required
def register():
    """
    Registrar un nuevo vehículo
    ---
    tags:
      - Vehículos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - duenio_id
            - matricula
            - marca
            - modelo
            - anio
          properties:
            duenio_id:
              type: integer
              example: 1
              description: ID del dueño del vehículo
            matricula:
              type: string
              example: ABC123
            marca:
              type: string
              example: Toyota
            modelo:
              type: string
              example: Corolla
            anio:
              type: integer
              example: 2020
              minimum: 1900
              maximum: 2100
    responses:
      201:
        description: Vehículo registrado exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
            matricula:
              type: string
            marca:
              type: string
            modelo:
              type: string
            anio:
              type: integer
            estado:
              type: string
      400:
        description: Error en los datos o vehículo ya existe
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
    return register_vehicle()
    

@vehicles.route("/<string:matricula>", methods=['GET'])
@token_required
def profile(matricula: str):
    """
    Obtener perfil de vehículo por matrícula
    ---
    tags:
      - Vehículos
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
        description: Perfil del vehículo con información del dueño
        schema:
          type: object
          properties:
            id:
              type: integer
            matricula:
              type: string
            marca:
              type: string
            modelo:
              type: string
            anio:
              type: integer
            estado:
              type: string
            duenio_id:
              type: integer
            nombre_duenio:
              type: string
      400:
        description: Vehículo no encontrado o sin permisos
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
    return get_vehicle_profile(matricula)


@vehicles.route("", methods=['GET'])
@token_required
def listar():
    """
    Listar vehículos del sistema
    ---
    tags:
      - Vehículos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de vehículos según permisos del usuario
        schema:
          type: object
          properties:
            vehiculos:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  matricula:
                    type: string
                  marca:
                    type: string
                  modelo:
                    type: string
                  anio:
                    type: integer
                  estado:
                    type: string
                  duenio_id:
                    type: integer
                  nombre_duenio:
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
    return list_all_vehicles()


@vehicles.route("/<string:matricula>", methods=['PUT'])
@token_required
def actualizar(matricula: str):
    """
    Actualizar datos de un vehículo
    ---
    tags:
      - Vehículos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: matricula
        type: string
        required: true
        description: Matrícula del vehículo
      - in: body
        name: body
        required: true
        description: Al menos un campo debe ser proporcionado
        schema:
          type: object
          properties:
            marca:
              type: string
              example: Honda
            modelo:
              type: string
              example: Civic
            anio:
              type: integer
              example: 2021
              minimum: 1900
              maximum: 2100
    responses:
      200:
        description: Vehículo actualizado exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
            matricula:
              type: string
            marca:
              type: string
            modelo:
              type: string
            anio:
              type: integer
            estado:
              type: string
            duenio_id:
              type: integer
            nombre_duenio:
              type: string
      400:
        description: Vehículo no encontrado, INACTIVO, sin permisos o datos inválidos
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No se puede actualizar un vehículo INACTIVO"
      401:
        description: Token no proporcionado o inválido
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return update_vehicle(matricula)


@vehicles.route("/<string:matricula>", methods=['DELETE'])
@token_required
def desactivar(matricula: str):
    """
    Desactivar vehículo (soft delete)
    ---
    tags:
      - Vehículos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: matricula
        type: string
        required: true
        description: Matrícula del vehículo a desactivar
    responses:
      200:
        description: Vehículo desactivado exitosamente (estado cambiado a INACTIVO)
        schema:
          type: object
          properties:
            id:
              type: integer
            matricula:
              type: string
            marca:
              type: string
            modelo:
              type: string
            anio:
              type: integer
            estado:
              type: string
              example: INACTIVO
            duenio_id:
              type: integer
            nombre_duenio:
              type: string
      400:
        description: Vehículo no encontrado o ya está inactivo
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
    return delete_vehicle(matricula)


@vehicles.route("/<string:matricula>/bookings", methods=['GET'])
@token_required
def vehicle_bookings(matricula: str):
    """
    Listar turnos de un vehículo
    ---
    tags:
      - Vehículos
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
        description: Vehículo no encontrado o sin permisos
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


@vehicles.route("/<string:matricula>/inspections", methods=['GET'])
@token_required
def vehicle_inspections(matricula: str):
    """
    Listar inspecciones de un vehículo
    
    Autorización:
    - ADMIN e INSPECTOR: pueden ver inspecciones de cualquier vehículo
    - DUENIO: solo puede ver inspecciones de sus propios vehículos
    ---
    tags:
      - Vehículos
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
        description: Lista de inspecciones del vehículo
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
    return list_inspections_by_vehiculo(matricula)
