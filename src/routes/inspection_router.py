from flask import Blueprint
from src.utils.jwt_utils import token_required, role_required
from src.controllers.inspection_controller import (
    create_inspection,
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
    Crear una inspección completa con sus 8 chequeos
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
            - chequeos
          properties:
            turno_id:
              type: integer
              example: 1
              description: ID del turno confirmado para el cual se crea la inspección
            inspector_id:
              type: integer
              example: 2
              description: ID del inspector que realizó la inspección
            chequeos:
              type: array
              minItems: 8
              maxItems: 8
              description: Los 8 chequeos de la inspección técnica vehicular
              items:
                type: object
                required:
                  - descripcion
                  - puntuacion
                properties:
                  descripcion:
                    type: string
                    maxLength: 200
                    description: Descripción del chequeo
                  puntuacion:
                    type: integer
                    minimum: 1
                    maximum: 10
                    description: Puntuación del chequeo (1-10)
              example:
                - descripcion: "Luces y señalización"
                  puntuacion: 9
                - descripcion: "Frenos"
                  puntuacion: 8
                - descripcion: "Dirección y suspensión"
                  puntuacion: 10
                - descripcion: "Neumáticos"
                  puntuacion: 7
                - descripcion: "Chasis y estructura"
                  puntuacion: 9
                - descripcion: "Contaminación y ruidos"
                  puntuacion: 8
                - descripcion: "Elementos de seguridad obligatorios"
                  puntuacion: 10
                - descripcion: "Cinturones, vidrios y espejos"
                  puntuacion: 9
    responses:
      201:
        description: Inspección creada exitosamente con sus 8 chequeos
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
              description: Suma inicial (0) - se calcula al cerrar la inspección
            resultado:
              type: string
              nullable: true
            observacion:
              type: string
              nullable: true
            estado:
              type: string
              example: "EN_PROCESO"
            chequeos:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  descripcion:
                    type: string
                  puntuacion:
                    type: integer
                  fecha:
                    type: string
                    format: date-time
      400:
        description: Error en los datos proporcionados
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Token no proporcionado o inválido
      403:
        description: Usuario sin permisos (solo ADMIN e INSPECTOR)
    """
    return create_inspection()


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
    - SEGURO: suma >= 80 y ningún chequeo < 5
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
