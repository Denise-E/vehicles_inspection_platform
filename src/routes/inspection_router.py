from flask import Blueprint
from src.utils.jwt_utils import token_required, role_required
from src.controllers.inspection_controller import (
    create_inspection,
    register_chequeos,
    close_inspection,
    get_inspection,
    list_all_inspections
)

inspections = Blueprint('inspections', __name__)


@inspections.route("", methods=['POST'])
@token_required
@role_required('ADMIN', 'INSPECTOR')
def crear():
    """
    Crear una nueva inspección
    ---
    tags:
      - Inspecciones
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - turno_id
            - inspector_id
          properties:
            turno_id:
              type: integer
              example: 1
              description: ID del turno para el cual se crea la inspección
            inspector_id:
              type: integer
              example: 2
              description: ID del inspector que realizará la inspección
    responses:
      201:
        description: Inspección creada exitosamente
        schema:
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
      400:
        description: Error en los datos proporcionados
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
      403:
        description: Usuario sin permisos (no es INSPECTOR)
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return create_inspection()


@inspections.route("/<int:inspeccion_id>/chequeos", methods=['POST'])
@token_required
@role_required('ADMIN', 'INSPECTOR')
def registrar_chequeos(inspeccion_id: int):
    """
    Registrar los 8 chequeos de una inspección
    ---
    tags:
      - Inspecciones
    security:
      - Bearer: []
    parameters:
      - in: path
        name: inspeccion_id
        type: integer
        required: true
        description: ID de la inspección
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - chequeos
          properties:
            chequeos:
              type: array
              minItems: 8
              maxItems: 8
              items:
                type: object
                required:
                  - item_numero
                  - descripcion
                  - puntuacion
                properties:
                  item_numero:
                    type: integer
                    minimum: 1
                    maximum: 8
                    example: 1
                  descripcion:
                    type: string
                    minLength: 3
                    maxLength: 200
                    example: "Frenos delanteros"
                  puntuacion:
                    type: integer
                    minimum: 1
                    maximum: 10
                    example: 8
    responses:
      200:
        description: Chequeos registrados exitosamente
        schema:
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
      400:
        description: Error en los datos proporcionados
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
      403:
        description: Usuario sin permisos (no es INSPECTOR)
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return register_chequeos(inspeccion_id)




@inspections.route("/<int:inspeccion_id>", methods=['GET'])
@token_required
def detalle(inspeccion_id: int):
    """
    Obtener detalles de una inspección
    
    Autorización:
    - ADMIN e INSPECTOR: pueden ver cualquier inspección
    - DUENIO: solo puede ver inspecciones de sus propios vehículos
    ---
    tags:
      - Inspecciones
    security:
      - Bearer: []
    parameters:
      - in: path
        name: inspeccion_id
        type: integer
        required: true
        description: ID de la inspección
    responses:
      200:
        description: Detalles de la inspección
        schema:
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
            chequeos:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  item_numero:
                    type: integer
                  descripcion:
                    type: string
                  puntuacion:
                    type: integer
                  fecha:
                    type: string
                    format: date-time
      400:
        description: Inspección no encontrada
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
    return get_inspection(inspeccion_id)


@inspections.route("/<int:inspeccion_id>", methods=['PATCH'])
@token_required
@role_required('ADMIN', 'INSPECTOR')
def cerrar(inspeccion_id: int):
    """
    Cerrar una inspección y calcular resultado
    
    Reglas de negocio:
    - SEGURO: suma > 80 y ningún chequeo < 5
    - RECHEQUEAR: suma < 40 o algún chequeo < 5
    - Si RECHEQUEAR, observación es obligatoria (mínimo 10 caracteres)
    ---
    tags:
      - Inspecciones
    security:
      - Bearer: []
    parameters:
      - in: path
        name: inspeccion_id
        type: integer
        required: true
        description: ID de la inspección a cerrar
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            observacion:
              type: string
              minLength: 10
              maxLength: 500
              example: "Problemas detectados en frenos delanteros y luces traseras que requieren atención inmediata"
    responses:
      200:
        description: Inspección cerrada exitosamente
        schema:
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
              enum: [SEGURO, RECHEQUEAR]
            observacion:
              type: string
            estado:
              type: string
            chequeos:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  item_numero:
                    type: integer
                  descripcion:
                    type: string
                  puntuacion:
                    type: integer
                  fecha:
                    type: string
                    format: date-time
      400:
        description: Error en los datos proporcionados (ej. falta observación para RECHEQUEAR)
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
      403:
        description: Usuario sin permisos (no es INSPECTOR)
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return close_inspection(inspeccion_id)






@inspections.route("", methods=['GET'])
@token_required
@role_required('ADMIN')
def listar_todas():
    """
    Listar todas las inspecciones del sistema
    ---
    tags:
      - Inspecciones
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de todas las inspecciones
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
      401:
        description: Token no proporcionado o inválido
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return list_all_inspections()
