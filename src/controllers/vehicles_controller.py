from src.services.vehicle_service import VehicleService
from src.schemas.vehicle_schemas import VehicleRegisterRequest, VehicleResponse
from flask import request, jsonify


def register_vehicle(duenio_id: int) -> VehicleResponse:
    try:
        data = VehicleRegisterRequest(**request.json)
        vehicle = VehicleService.create_vehicle(data.model_dump(), duenio_id)
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
    except Exception as e:
        return jsonify({"error": str(e)}), 400
