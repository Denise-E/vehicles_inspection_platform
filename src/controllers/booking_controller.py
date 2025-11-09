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
    """
    Consulta los slots disponibles del sistema (disponibilidad general).
    
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Validar request body con Pydantic (puede ser vacío)
        request_data = request.json if request.json else {}
        data = DisponibilidadRequest(**request_data)
        
        # Validar rango de fechas si aplica
        data.validate_fecha_range()
        
        # Consultar disponibilidad general del sistema
        disponibilidad = BookingService.consultar_disponibilidad(
            data.fecha_inicio,
            data.fecha_final
        )
        
        # Validar response con Pydantic
        response = DisponibilidadResponse(**disponibilidad)
        return jsonify(response.model_dump()), 200
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def reservar_turno() -> Tuple[dict, int]:
    """
    Crea un nuevo turno en estado RESERVADO.
    
    Validaciones por rol:
    - ADMIN: Puede crear turnos para cualquier vehículo
    - Otros roles: Solo pueden crear turnos para sus propios vehículos
    
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Validar request body con Pydantic
        data = BookingCreateRequest(**request.json)
        
        # Obtener información del usuario del token JWT
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        booking_data = data.model_dump()
        booking_data['creado_por'] = user_id  
        
        # Crear turno con validación de autorización por rol
        turno = BookingService.create_booking(booking_data, user_role=user_role)
        
        # Preparar response
        response_data = {
            "id": turno.id,
            "vehiculo_id": turno.vehiculo_id,
            "matricula": turno.vehiculo.matricula,
            "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
            "estado": turno.estado.nombre,
            "creado_por": turno.creado_por,
            "nombre_creador": turno.creador.nombre_completo
        }
        
        # Validar response con Pydantic
        response = BookingResponse(**response_data)
        return jsonify(response.model_dump()), 201
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def actualizar_turno(turno_id: int) -> Tuple[dict, int]:
    """
    Actualiza el estado de un turno.
    
    Args:
        turno_id: ID del turno a actualizar
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Validar request body con Pydantic
        data = BookingUpdateRequest(**request.json)
        
        # Obtener información del usuario del token JWT
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        # Actualizar estado del turno con validación de autorización
        turno = BookingService.update_booking_status(
            turno_id, 
            data.estado_id,
            user_id=user_id,
            user_role=user_role
        )
        
        # Preparar response
        response_data = {
            "id": turno.id,
            "vehiculo_id": turno.vehiculo_id,
            "matricula": turno.vehiculo.matricula,
            "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
            "estado": turno.estado.nombre,
            "creado_por": turno.creado_por,
            "nombre_creador": turno.creador.nombre_completo
        }
        
        # Validar response con Pydantic
        response = BookingResponse(**response_data)
        return jsonify(response.model_dump()), 200
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def obtener_turno(turno_id: int) -> Tuple[dict, int]:
    """
    Obtiene los detalles de un turno por ID.
    
    Args:
        turno_id: ID del turno
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        turno = BookingService.get_booking_by_id(turno_id, user_id=user_id, user_role=user_role)
        
        # Preparar response
        response_data = {
            "id": turno.id,
            "vehiculo_id": turno.vehiculo_id,
            "matricula": turno.vehiculo.matricula,
            "fecha": turno.fecha.strftime('%Y-%m-%d %H:%M'),
            "estado": turno.estado.nombre,
            "creado_por": turno.creado_por,
            "nombre_creador": turno.creador.nombre_completo
        }
        
        # Validar response con Pydantic
        response = BookingResponse(**response_data)
        return jsonify(response.model_dump()), 200
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_turnos_por_usuario() -> Tuple[dict, int]:
    """
    Lista todos los turnos del usuario autenticado (obtenido del token JWT).
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        user_id = request.current_user['user_id']
        
        turnos = BookingService.list_bookings_by_user(user_id)
        
        # Preparar response
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
        
        # Validar response con Pydantic
        response = BookingListResponse(**response_data)
        return jsonify(response.model_dump()), 200
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_turnos_por_vehiculo(matricula: str) -> Tuple[dict, int]:
    """
    Lista todos los turnos de un vehículo.
    
    Args:
        matricula: Matrícula del vehículo
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Obtener turnos
        turnos = BookingService.list_bookings_by_vehicle(matricula)
        
        # Preparar response
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
        
        # Validar response con Pydantic
        response = BookingListResponse(**response_data)
        return jsonify(response.model_dump()), 200
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_todos_los_turnos() -> Tuple[dict, int]:
    """
    Lista todos los turnos del sistema.
    
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Obtener todos los turnos
        turnos = BookingService.list_all_bookings()
        
        # Preparar response
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
        
        # Validar response con Pydantic
        response = BookingListResponse(**response_data)
        return jsonify(response.model_dump()), 200
        
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400

