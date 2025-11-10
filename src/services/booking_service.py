from src import db
from src.models import Turno, Vehiculo, Usuario, EstadoTurno
from datetime import datetime, timedelta
from typing import Optional


# Configuración de horarios disponibles
HORARIO_CONFIG = {
    "dias_laborables": [0, 1, 2, 3, 4],  # Lunes=0 a Viernes=4
    "hora_inicio": 9,
    "hora_fin": 20,
    "duracion_turno_horas": 1,
    "dias_anticipacion": 15  # Mostrar disponibilidad para los próximos 15 días
}


class BookingService:

    @staticmethod
    def consultar_disponibilidad(fecha_inicio: Optional[str] = None, fecha_final: Optional[str] = None) -> dict:
        """
        Consulta los slots disponibles del sistema (disponibilidad general).
        
        Args:
            fecha_inicio: Fecha desde la cual buscar (formato YYYY-MM-DD), por defecto hoy
            fecha_final: Fecha hasta la cual buscar (formato YYYY-MM-DD), opcional
        """
        if fecha_inicio:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        else:
            inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if fecha_final:
            final = datetime.strptime(fecha_final, '%Y-%m-%d')
            if final < inicio:
                raise ValueError("fecha_final debe ser posterior o igual a fecha_inicio")
        else:
            final = inicio + timedelta(days=HORARIO_CONFIG["dias_anticipacion"])
        
        slots = []
        fecha_actual = inicio
        
        while fecha_actual <= final:
            # Solo días laborables (lunes a viernes)
            if fecha_actual.weekday() in HORARIO_CONFIG["dias_laborables"]:
                # Generar slots por hora
                for hora in range(HORARIO_CONFIG["hora_inicio"], HORARIO_CONFIG["hora_fin"]):
                    slot_datetime = fecha_actual.replace(hour=hora, minute=0, second=0, microsecond=0)
                    
                    if slot_datetime > datetime.now():
                        # Verificar si hay algún turno confirmado o reservado en ese horario
                        turno_existente = Turno.query.filter(
                            Turno.fecha == slot_datetime,
                            Turno.estado_id.in_([1, 2])  # RESERVADO=1 o CONFIRMADO=2
                        ).first()
                        
                        slots.append({
                            "fecha": slot_datetime.strftime('%Y-%m-%d %H:%M'),
                            "disponible": turno_existente is None
                        })
            
            fecha_actual += timedelta(days=1)
        
        return {
            "slots": slots,
            "total_disponibles": sum(1 for slot in slots if slot["disponible"])
        }

    @staticmethod
    def create_booking(data: dict, user_role: str = None) -> Turno:
        """
        Crea un nuevo turno.
        """
        vehiculo = Vehiculo.query.filter_by(matricula=data["matricula"]).first()
        if not vehiculo:
            raise ValueError(f"Vehículo con matrícula {data['matricula']} no encontrado")
        
        usuario = Usuario.query.filter_by(id=data["creado_por"]).first()
        if not usuario:
            raise ValueError(f"Usuario con ID {data['creado_por']} no encontrado")
        
        if vehiculo.estado_id == 2:  # 2 = INACTIVO
            raise ValueError("No se puede crear un turno para un vehículo INACTIVO")
        
        if user_role != 'ADMIN':
            if vehiculo.duenio_id != data["creado_por"]:
                raise ValueError("No tienes permiso para crear turnos para este vehículo. Solo puedes crear turnos para tus propios vehículos")
        
        fecha_turno = datetime.strptime(data["fecha"], '%Y-%m-%d %H:%M')
        
        if fecha_turno <= datetime.now():
            raise ValueError("La fecha del turno debe ser futura")
        
        # Validar día y horario laborable
        if fecha_turno.weekday() not in HORARIO_CONFIG["dias_laborables"]:
            raise ValueError("Los turnos solo pueden ser de lunes a viernes")
        
        if not (HORARIO_CONFIG["hora_inicio"] <= fecha_turno.hour < HORARIO_CONFIG["hora_fin"]):
            raise ValueError(f"Los turnos solo pueden ser entre las {HORARIO_CONFIG['hora_inicio']}:00 y las {HORARIO_CONFIG['hora_fin']}:00")
        
        # Verificar que no exista otro turno para ese vehículo en esa fecha
        turno_existente = Turno.query.filter(
            Turno.vehiculo_id == vehiculo.id,
            Turno.fecha == fecha_turno,
            Turno.estado_id.in_([1, 2])  # RESERVADO o CONFIRMADO
        ).first()
        
        if turno_existente:
            raise ValueError("Ya existe un turno para este vehículo en esa fecha y hora")
        
        estado_reservado = EstadoTurno.query.filter_by(nombre="RESERVADO").first()
        if not estado_reservado:
            raise ValueError("Estado RESERVADO no encontrado en la base de datos")
        
        nuevo_turno = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_reservado.id,
            creado_por=data["creado_por"]
        )
        
        db.session.add(nuevo_turno)
        db.session.commit()
        db.session.refresh(nuevo_turno, ['vehiculo', 'estado', 'creador'])
        
        return nuevo_turno

    @staticmethod
    def update_booking_status(turno_id: int, nuevo_estado_id: int, user_id: int = None, user_role: str = None) -> Turno:
        """
        Actualiza el estado de un turno.
        
        Reglas de negocio:
        - Estados COMPLETADO (3) y CANCELADO (4) son finales, no permiten cambios
        - ADMIN puede modificar cualquier turno (excepto los que están en estados finales)
        - Usuarios normales solo pueden modificar turnos de vehículos que les pertenecen
        
        Transiciones de estado válidas:
        - RESERVADO (1) → CONFIRMADO (2) o CANCELADO (4)
        - CONFIRMADO (2) → COMPLETADO (3) o CANCELADO (4)
        - COMPLETADO (3) → No permite cambios
        - CANCELADO (4) → No permite cambios
        """
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        # Estado 3 = COMPLETADO. Estado 4 = CANCELADO
        if turno.estado_id in [3, 4]:
            raise ValueError(f"No se puede modificar un turno en estado {turno.estado.nombre}")
        
        if user_role != 'ADMIN':
            if turno.vehiculo.duenio_id != user_id:
                raise ValueError("No tienes permiso para modificar este turno. Solo puedes modificar turnos de tus propios vehículos")
        
        nuevo_estado = EstadoTurno.query.filter_by(id=nuevo_estado_id).first()
        if not nuevo_estado:
            raise ValueError(f"Estado con ID {nuevo_estado_id} no encontrado")
        
        estado_actual = turno.estado.nombre
        estado_nuevo = nuevo_estado.nombre
        
        transiciones_validas = {
            "RESERVADO": ["CONFIRMADO", "CANCELADO"],
            "CONFIRMADO": ["COMPLETADO", "CANCELADO"],
            "COMPLETADO": [],  # Estado final, no permite cambios
            "CANCELADO": []    # Estado final, no permite cambios
        }
        
        if estado_nuevo not in transiciones_validas.get(estado_actual, []):
            raise ValueError(
                f"Transición de estado inválida: {estado_actual} → {estado_nuevo}. "
                f"Transiciones permitidas desde {estado_actual}: {', '.join(transiciones_validas.get(estado_actual, [])) or 'ninguna'}"
            )
        
        turno.estado_id = nuevo_estado_id
        db.session.commit()
        db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turno

    @staticmethod
    def get_booking_by_id(turno_id: int, user_id: int = None, user_role: str = None) -> Turno:
        """
        Obtiene un turno por su ID.
        
        Reglas de autorización:
        - ADMIN puede ver cualquier turno
        - Usuarios normales solo pueden ver turnos de sus propios vehículos
        """
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        if user_role != 'ADMIN':
            if turno.vehiculo.duenio_id != user_id:
                raise ValueError("No tienes permiso para ver este turno. Solo puedes ver turnos de tus propios vehículos")
        
        db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        return turno

    @staticmethod
    def list_bookings_by_user(user_id: int) -> list[Turno]:
        """
        Lista todos los turnos creados por un usuario.
        """
        usuario = Usuario.query.filter_by(id=user_id).first()
        if not usuario:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        
        turnos = Turno.query.filter_by(creado_por=user_id).order_by(Turno.fecha.desc()).all()
        
        # Carga relaciones
        for turno in turnos:
            db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turnos

    @staticmethod
    def list_bookings_by_vehicle(matricula: str, user_id: int = None, user_role: str = None) -> list[Turno]:
        """
        Lista todos los turnos de un vehículo.
        - ADMIN e INSPECTOR: pueden ver turnos de cualquier vehículo
        - DUENIO: solo puede ver turnos de sus propios vehículos
        """
        vehiculo = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehiculo:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        if user_role and user_role not in ["ADMIN", "INSPECTOR"]:
            if vehiculo.duenio_id != user_id:
                raise ValueError("No tiene permisos para ver los turnos de este vehículo")
        
        turnos = Turno.query.filter_by(vehiculo_id=vehiculo.id).order_by(Turno.fecha.desc()).all()
        
        # Carga relaciones
        for turno in turnos:
            db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turnos

    @staticmethod
    def list_all_bookings(user_id: int = None, user_role: str = None) -> list[Turno]:
        """
        Lista turnos del sistema.
        - ADMIN: ve todos los turnos
        - DUENIO: solo ve turnos de sus propios vehículos
        """
        if user_role == "ADMIN":
            turnos = Turno.query.order_by(Turno.fecha.desc()).all()
        else:
            turnos = (Turno.query
                     .join(Vehiculo)
                     .filter(Vehiculo.duenio_id == user_id)
                     .order_by(Turno.fecha.desc())
                     .all())
        
        for turno in turnos:
            db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turnos
