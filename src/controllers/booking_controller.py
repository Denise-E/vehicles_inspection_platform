from src.services.booking_service import BookingService
from src.schemas.booking_schemas import (
    DisponibilidadRequest,
    DisponibilidadResponse,
    BookingCreateRequest,
    BookingUpdateRequest,
    BookingResponse,
    BookingListResponse
)
from flask import request, jsonify
from typing import Tuple
from pydantic import ValidationError


def consultar_disponibilidad() -> Tuple[dict, int]:
    try:
        request_data = request.json if request.json else {}
        data = DisponibilidadRequest(**request_data)
        
        data.validate_fecha_range()
        
        disponibilidad = BookingService.consultar_disponibilidad(
            data.fecha_inicio,
            data.fecha_final
        )
        
        response = DisponibilidadResponse(**disponibilidad)
        return jsonify(response.model_dump()), 200 
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def reservar_turno() -> Tuple[dict, int]:
    """
    Validaciones por rol:
    - ADMIN: Puede crear turnos para cualquier vehículo
    - Otros roles: Solo pueden crear turnos para sus propios vehículos
    """
    try:
        data = BookingCreateRequest(**request.json)
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        booking_data = data.model_dump()
        booking_data['creado_por'] = user_id  
        
        turno = BookingService.create_booking(booking_data, user_role=user_role)
        
        response_data = {
            "id": turno.id,
            "vehiculo_id": turno.vehiculo_id,
            "matricula": turno.vehiculo.matricula,
            "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
            "estado": turno.estado.nombre,
            "creado_por": turno.creado_por,
            "nombre_creador": turno.creador.nombre_completo
        }
        
        response = BookingResponse(**response_data)
        return jsonify(response.model_dump()), 201  
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def actualizar_turno(turno_id: int) -> Tuple[dict, int]:
    try:
        data = BookingUpdateRequest(**request.json)
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        turno = BookingService.update_booking_status(
            turno_id, 
            data.estado_id,
            user_id=user_id,
            user_role=user_role
        )
        
        response_data = {
            "id": turno.id,
            "vehiculo_id": turno.vehiculo_id,
            "matricula": turno.vehiculo.matricula,
            "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
            "estado": turno.estado.nombre,
            "creado_por": turno.creado_por,
            "nombre_creador": turno.creador.nombre_completo
        }
        
        response = BookingResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def obtener_turno(turno_id: int) -> Tuple[dict, int]:
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        turno = BookingService.get_booking_by_id(turno_id, user_id=user_id, user_role=user_role)
        
        response_data = {
            "id": turno.id,
            "vehiculo_id": turno.vehiculo_id,
            "matricula": turno.vehiculo.matricula,
            "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
            "estado": turno.estado.nombre,
            "creado_por": turno.creado_por,
            "nombre_creador": turno.creador.nombre_completo
        }
        
        response = BookingResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_turnos_por_usuario() -> Tuple[dict, int]:
    """
    Lista todos los turnos del usuario autenticado.
    """
    try:
        user_id = request.current_user['user_id']
        
        turnos = BookingService.list_bookings_by_user(user_id)
        
        turnos_data = []
        for turno in turnos:
            turnos_data.append({
                "id": turno.id,
                "vehiculo_id": turno.vehiculo_id,
                "matricula": turno.vehiculo.matricula,
                "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
                "estado": turno.estado.nombre,
                "creado_por": turno.creado_por,
                "nombre_creador": turno.creador.nombre_completo
            })
        
        response_data = {
            "turnos": turnos_data,
            "total": len(turnos_data)
        }
        
        response = BookingListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_turnos_por_vehiculo(matricula: str) -> Tuple[dict, int]:
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        turnos = BookingService.list_bookings_by_vehicle(matricula, user_id=user_id, user_role=user_role)
        
        turnos_data = []
        for turno in turnos:
            turnos_data.append({
                "id": turno.id,
                "vehiculo_id": turno.vehiculo_id,
                "matricula": turno.vehiculo.matricula,
                "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
                "estado": turno.estado.nombre,
                "creado_por": turno.creado_por,
                "nombre_creador": turno.creador.nombre_completo
            })
        
        response_data = {
            "turnos": turnos_data,
            "total": len(turnos_data)
        }
        
        response = BookingListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_todos_los_turnos() -> Tuple[dict, int]:
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        turnos = BookingService.list_all_bookings(user_id=user_id, user_role=user_role)
        
        turnos_data = []
        for turno in turnos:
            turnos_data.append({
                "id": turno.id,
                "vehiculo_id": turno.vehiculo_id,
                "matricula": turno.vehiculo.matricula,
                "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
                "estado": turno.estado.nombre,
                "creado_por": turno.creado_por,
                "nombre_creador": turno.creador.nombre_completo
            })
        
        response_data = {
            "turnos": turnos_data,
            "total": len(turnos_data)
        }
        
        response = BookingListResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400

