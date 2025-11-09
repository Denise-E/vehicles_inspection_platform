from src.services.booking_service import BookingService
from src.schemas.booking_schemas import (
    DisponibilidadRequest,
    DisponibilidadResponse,
    BookingCreateRequest,
    BookingResponse,
    BookingListResponse,
    SlotDisponible
)
from flask import request, jsonify
from typing import Tuple


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
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def reservar_turno() -> Tuple[dict, int]:
    """
    Crea un nuevo turno en estado RESERVADO.
    
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Validar request body con Pydantic
        data = BookingCreateRequest(**request.json)
        
        # Crear turno
        turno = BookingService.create_booking(data.model_dump())
        
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
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def confirmar_turno(turno_id: int) -> Tuple[dict, int]:
    """
    Confirma un turno (cambia estado a CONFIRMADO).
    
    Args:
        turno_id: ID del turno a confirmar
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Confirmar turno
        turno = BookingService.confirmar_booking(turno_id)
        
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
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def cancelar_turno(turno_id: int) -> Tuple[dict, int]:
    """
    Cancela un turno (cambia estado a CANCELADO).
    
    Args:
        turno_id: ID del turno a cancelar
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Cancelar turno
        turno = BookingService.cancelar_booking(turno_id)
        
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
        # Obtener turno
        turno = BookingService.get_booking_by_id(turno_id)
        
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
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def listar_turnos_por_usuario(user_id: int) -> Tuple[dict, int]:
    """
    Lista todos los turnos de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Tuple con (response_json, status_code)
    """
    try:
        # Obtener turnos
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
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

