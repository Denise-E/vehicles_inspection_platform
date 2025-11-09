from src.services.inspection_service import InspectionService
from src.schemas.inspection_schemas import (
    InspectionCreateRequest,
    InspectionResponse,
    InspectionDetailResponse,
    ChequeosListRequest,
    InspectionCloseRequest,
    InspectionListResponse
)
from flask import request, jsonify
from typing import Tuple
from pydantic import ValidationError


def create_inspection() -> Tuple[dict, int]:
    """
    Crea una nueva inspección asociada a un turno.
    Solo usuarios con rol INSPECTOR pueden crear inspecciones.
    """
    try:
        data = InspectionCreateRequest(**request.json)
        inspection = InspectionService.create_inspection(data.model_dump())
        
        response_data = {
            "id": inspection.id,
            "turno_id": inspection.turno_id,
            "vehiculo_matricula": inspection.vehiculo.matricula,
            "inspector_nombre": inspection.inspector.nombre_completo,
            "fecha": inspection.fecha,
            "puntuacion_total": inspection.puntuacion_total,
            "resultado": inspection.resultado.nombre if inspection.resultado else None,
            "observacion": inspection.observacion,
            "estado": inspection.estado
        }
        response = InspectionResponse(**response_data)
        return jsonify(response.model_dump()), 201
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def register_chequeos(inspeccion_id: int) -> Tuple[dict, int]:
    """
    Registra los 8 chequeos de una inspección.
    """
    try:
        data = ChequeosListRequest(**request.json)
        
        # Extraer solo los datos necesarios de cada chequeo
        chequeos_data = [chequeo.model_dump() for chequeo in data.chequeos]
        
        inspection = InspectionService.register_chequeos(inspeccion_id, chequeos_data)
        
        response_data = {
            "id": inspection.id,
            "turno_id": inspection.turno_id,
            "vehiculo_matricula": inspection.vehiculo.matricula,
            "inspector_nombre": inspection.inspector.nombre_completo,
            "fecha": inspection.fecha,
            "puntuacion_total": inspection.puntuacion_total,
            "resultado": inspection.resultado.nombre if inspection.resultado else None,
            "observacion": inspection.observacion,
            "estado": inspection.estado
        }
        response = InspectionResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def close_inspection(inspeccion_id: int) -> Tuple[dict, int]:
    """
    Cierra una inspección, calcula el resultado y actualiza el estado del vehículo.
    Solo usuarios con rol INSPECTOR pueden cerrar inspecciones.
    """
    try:
        data = InspectionCloseRequest(**request.json)
        inspection = InspectionService.close_inspection(inspeccion_id, data.observacion)
        
        # Preparar chequeos para respuesta
        chequeos_response = []
        for idx, chequeo in enumerate(inspection.chequeos, start=1):
            chequeos_response.append({
                "id": chequeo.id,
                "item_numero": idx,
                "descripcion": f"Chequeo {idx}",
                "puntuacion": chequeo.puntuacion,
                "fecha": chequeo.fecha
            })
        
        response_data = {
            "id": inspection.id,
            "turno_id": inspection.turno_id,
            "vehiculo_matricula": inspection.vehiculo.matricula,
            "inspector_nombre": inspection.inspector.nombre_completo,
            "fecha": inspection.fecha,
            "puntuacion_total": inspection.puntuacion_total,
            "resultado": inspection.resultado.nombre if inspection.resultado else None,
            "observacion": inspection.observacion,
            "estado": inspection.estado,
            "chequeos": chequeos_response
        }
        response = InspectionDetailResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_inspection(inspeccion_id: int) -> Tuple[dict, int]:
    """
    Obtiene una inspección por su ID con todos sus chequeos.
    """
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        inspection = InspectionService.get_inspection_by_id(inspeccion_id, user_id=user_id, user_role=user_role)
        
        # Preparar chequeos para respuesta
        chequeos_response = []
        for idx, chequeo in enumerate(inspection.chequeos, start=1):
            chequeos_response.append({
                "id": chequeo.id,
                "item_numero": idx,
                "descripcion": f"Chequeo {idx}",
                "puntuacion": chequeo.puntuacion,
                "fecha": chequeo.fecha
            })
        
        response_data = {
            "id": inspection.id,
            "turno_id": inspection.turno_id,
            "vehiculo_matricula": inspection.vehiculo.matricula,
            "inspector_nombre": inspection.inspector.nombre_completo,
            "fecha": inspection.fecha,
            "puntuacion_total": inspection.puntuacion_total,
            "resultado": inspection.resultado.nombre if inspection.resultado else None,
            "observacion": inspection.observacion,
            "estado": inspection.estado,
            "chequeos": chequeos_response
        }
        response = InspectionDetailResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def list_inspections_by_vehiculo(matricula: str) -> Tuple[dict, int]:
    """
    Lista todas las inspecciones de un vehículo por matrícula.
    
    Validaciones de autorización:
    - ADMIN e INSPECTOR pueden ver inspecciones de cualquier vehículo
    - DUENIO solo puede ver inspecciones de sus propios vehículos
    """
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        inspections = InspectionService.list_inspections_by_vehiculo(matricula, user_id=user_id, user_role=user_role)
        
        inspections_data = []
        for inspection in inspections:
            inspections_data.append({
                "id": inspection.id,
                "turno_id": inspection.turno_id,
                "vehiculo_matricula": inspection.vehiculo.matricula,
                "inspector_nombre": inspection.inspector.nombre_completo,
                "fecha": inspection.fecha,
                "puntuacion_total": inspection.puntuacion_total,
                "resultado": inspection.resultado.nombre if inspection.resultado else None,
                "observacion": inspection.observacion,
                "estado": inspection.estado
            })
        
        response_data = {
            "inspecciones": inspections_data,
            "total": len(inspections_data)
        }
        response = InspectionListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def list_inspections_by_inspector(inspector_id: int) -> Tuple[dict, int]:
    """
    Lista todas las inspecciones realizadas por un inspector.
    
    Validaciones de autorización:
    - ADMIN puede ver inspecciones de cualquier inspector
    - INSPECTOR solo puede ver sus propias inspecciones
    """
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        inspections = InspectionService.list_inspections_by_inspector(inspector_id, user_id=user_id, user_role=user_role)
        
        inspections_data = []
        for inspection in inspections:
            inspections_data.append({
                "id": inspection.id,
                "turno_id": inspection.turno_id,
                "vehiculo_matricula": inspection.vehiculo.matricula,
                "inspector_nombre": inspection.inspector.nombre_completo,
                "fecha": inspection.fecha,
                "puntuacion_total": inspection.puntuacion_total,
                "resultado": inspection.resultado.nombre if inspection.resultado else None,
                "observacion": inspection.observacion,
                "estado": inspection.estado
            })
        
        response_data = {
            "inspecciones": inspections_data,
            "total": len(inspections_data)
        }
        response = InspectionListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def list_all_inspections() -> Tuple[dict, int]:
    """
    Lista todas las inspecciones del sistema.
    """
    try:
        inspections = InspectionService.list_all_inspections()
        
        inspections_data = []
        for inspection in inspections:
            inspections_data.append({
                "id": inspection.id,
                "turno_id": inspection.turno_id,
                "vehiculo_matricula": inspection.vehiculo.matricula,
                "inspector_nombre": inspection.inspector.nombre_completo,
                "fecha": inspection.fecha,
                "puntuacion_total": inspection.puntuacion_total,
                "resultado": inspection.resultado.nombre if inspection.resultado else None,
                "observacion": inspection.observacion,
                "estado": inspection.estado
            })
        
        response_data = {
            "inspecciones": inspections_data,
            "total": len(inspections_data)
        }
        response = InspectionListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400

