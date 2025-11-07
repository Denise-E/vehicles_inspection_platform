from flask import Blueprint
from src.utils.jwt_utils import token_required
from src.controllers.vehicles_controller import (
    register_vehicle,
    get_vehicle_profile,
    list_all_vehicles,
    update_vehicle,
    delete_vehicle
)

vehicles = Blueprint('vehicles', __name__)


@vehicles.route("/register/<int:duenio_id>", methods=['POST'])
@token_required
def register(duenio_id: int):
    """
    Registrar un nuevo vehículo
    ---
    tags:
      - Vehículos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: duenio_id
        type: integer
        required: true
        description: ID del dueño del vehículo
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - matricula
            - marca
            - modelo
            - anio
          properties:
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
    return register_vehicle(duenio_id)
    

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
    return get_vehicle_profile(matricula)


@vehicles.route("", methods=['GET'])
@token_required
def listar():
    """
    Listar todos los vehículos
    ---
    tags:
      - Vehículos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de todos los vehículos del sistema
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
        schema:
          type: object
          required:
            - marca
            - modelo
            - anio
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
        description: Vehículo no encontrado o datos inválidos
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
    return update_vehicle(matricula)


@vehicles.route("/delete/<string:matricula>", methods=['PATCH'])
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
