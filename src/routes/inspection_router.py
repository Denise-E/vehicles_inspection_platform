from flask import Blueprint
from src.utils.jwt_utils import token_required, role_required
from src.controllers.inspection_controller import (
    create_inspection,
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
    
    Reglas de negocio:
    - SEGURO: 40 ≤ puntos ≤ 80 Y todos los chequeos ≥ 5
    - RECHEQUEAR: puntos < 40 O algún chequeo < 5 (observación OBLIGATORIA)
    - La inspección debe realizarse el día programado del turno
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
            observacion:
              type: string
              minLength: 10
              maxLength: 500
              required: false
              description: "Observación sobre la inspección (obligatoria si resultado será RECHEQUEAR)"
              example: "Todos los sistemas funcionan correctamente"
    responses:
      201:
        description: Inspección creada y cerrada exitosamente
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
              description: Suma total de las puntuaciones de los 8 chequeos
             resultado:
               type: string
               enum: [SEGURO, RECHEQUEAR]
               description: "SEGURO si 40 ≤ puntos ≤ 80 Y todos >= 5, sino RECHEQUEAR"
            observacion:
              type: string
              description: "Observación obligatoria para resultado RECHEQUEAR"
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
