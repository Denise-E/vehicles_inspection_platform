from src.services.vehicle_service import VehicleService
from src.schemas.vehicle_schemas import (
    VehicleRegisterRequest,
    VehicleUpdateRequest,
    VehicleResponse,
    VehicleDetailResponse,
    VehicleListResponse
)
from flask import request, jsonify
from typing import Tuple
from pydantic import ValidationError


def register_vehicle() -> Tuple[dict, int]:
    """
    Registra un nuevo vehículo.
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        data = VehicleRegisterRequest(**request.json)
        vehicle = VehicleService.create_vehicle(data.model_dump(), data.duenio_id)
        
        response_data = {
            "id": vehicle.id,
            "matricula": vehicle.matricula,
            "marca": vehicle.marca,
            "modelo": vehicle.modelo,
            "anio": vehicle.anio,
            "estado": vehicle.estado.nombre
        }
        
        response = VehicleResponse(**response_data)
        return jsonify(response.model_dump()), 201        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_vehicle_profile(matricula: str) -> Tuple[dict, int]:
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        vehicle = VehicleService.get_vehicle_by_matricula(matricula, user_id=user_id, user_role=user_role)
        
        response_data = {
            "id": vehicle.id,
            "matricula": vehicle.matricula,
            "marca": vehicle.marca,
            "modelo": vehicle.modelo,
            "anio": vehicle.anio,
            "estado": vehicle.estado.nombre,
            "duenio_id": vehicle.duenio_id,
            "nombre_duenio": vehicle.duenio.nombre_completo
        }
        
        response = VehicleDetailResponse(**response_data)
        return jsonify(response.model_dump()), 200        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def list_all_vehicles() -> Tuple[dict, int]:
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        vehicles = VehicleService.list_all_vehicles(user_id=user_id, user_role=user_role)
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                "id": vehicle.id,
                "matricula": vehicle.matricula,
                "marca": vehicle.marca,
                "modelo": vehicle.modelo,
                "anio": vehicle.anio,
                "estado": vehicle.estado.nombre,
                "duenio_id": vehicle.duenio_id,
                "nombre_duenio": vehicle.duenio.nombre_completo
            })
        
        response_data = {
            "vehiculos": vehicles_data,
            "total": len(vehicles_data)
        }
        
        response = VehicleListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def update_vehicle(matricula: str) -> Tuple[dict, int]:
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        data = VehicleUpdateRequest(**request.json)
        
        vehicle = VehicleService.update_vehicle(
            matricula, 
            data.model_dump(exclude_none=True),
            user_id=user_id,
            user_role=user_role
        )
        
        response_data = {
            "id": vehicle.id,
            "matricula": vehicle.matricula,
            "marca": vehicle.marca,
            "modelo": vehicle.modelo,
            "anio": vehicle.anio,
            "estado": vehicle.estado.nombre,
            "duenio_id": vehicle.duenio_id,
            "nombre_duenio": vehicle.duenio.nombre_completo
        }
        
        response = VehicleDetailResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def delete_vehicle(matricula: str) -> Tuple[dict, int]:
    """
    Elimina un vehículo (soft delete - cambia estado a INACTIVO).
    """
    try:
        vehicle = VehicleService.delete_vehicle(matricula)
        
        response_data = {
            "id": vehicle.id,
            "matricula": vehicle.matricula,
            "marca": vehicle.marca,
            "modelo": vehicle.modelo,
            "anio": vehicle.anio,
            "estado": vehicle.estado.nombre,
            "duenio_id": vehicle.duenio_id,
            "nombre_duenio": vehicle.duenio.nombre_completo
        }
        
        response = VehicleDetailResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400
