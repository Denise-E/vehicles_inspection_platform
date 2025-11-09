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
        
        Returns:
            dict con slots disponibles
        """
        # Determinar fecha de inicio
        if fecha_inicio:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        else:
            inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Determinar fecha final
        if fecha_final:
            final = datetime.strptime(fecha_final, '%Y-%m-%d')
            # Validar que fecha_final sea posterior a fecha_inicio
            if final < inicio:
                raise ValueError("fecha_final debe ser posterior o igual a fecha_inicio")
        else:
            # Por defecto, mostrar los próximos N días configurados
            final = inicio + timedelta(days=HORARIO_CONFIG["dias_anticipacion"])
        
        # Generar slots disponibles
        slots = []
        fecha_actual = inicio
        
        while fecha_actual <= final:
            # Solo días laborables (lunes a viernes)
            if fecha_actual.weekday() in HORARIO_CONFIG["dias_laborables"]:
                # Generar slots por hora
                for hora in range(HORARIO_CONFIG["hora_inicio"], HORARIO_CONFIG["hora_fin"]):
                    slot_datetime = fecha_actual.replace(hour=hora, minute=0, second=0, microsecond=0)
                    
                    # Solo mostrar slots futuros
                    if slot_datetime > datetime.now():
                        # Verificar si hay algún turno confirmado o reservado en ese horario
                        # (sin importar el vehículo - disponibilidad general del sistema)
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
        Crea un nuevo turno (estado RESERVADO).
        
        Args:
            data: dict con matricula, fecha, creado_por
            user_role: Rol del usuario
            
        Returns:
            Turno creado
        """
        # Verificar que el vehículo existe
        vehiculo = Vehiculo.query.filter_by(matricula=data["matricula"]).first()
        if not vehiculo:
            raise ValueError(f"Vehículo con matrícula {data['matricula']} no encontrado")
        
        # Verificar que el usuario existe
        usuario = Usuario.query.filter_by(id=data["creado_por"]).first()
        if not usuario:
            raise ValueError(f"Usuario con ID {data['creado_por']} no encontrado")
        
        if user_role != 'ADMIN':
            if vehiculo.duenio_id != data["creado_por"]:
                raise ValueError("No tienes permiso para crear turnos para este vehículo. Solo puedes crear turnos para tus propios vehículos")
            
            if vehiculo.estado.nombre != 'ACTIVO':
                raise ValueError(f"No puedes crear turnos para un vehículo en estado {vehiculo.estado.nombre}. El vehículo debe estar ACTIVO")
        
        # Parsear fecha
        fecha_turno = datetime.strptime(data["fecha"], '%Y-%m-%d %H:%M')
        
        # Validar que la fecha sea futura
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
        
        # Obtener estado RESERVADO (id=1)
        estado_reservado = EstadoTurno.query.filter_by(nombre="RESERVADO").first()
        if not estado_reservado:
            raise ValueError("Estado RESERVADO no encontrado en la base de datos")
        
        # Crear turno
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
    def update_booking_status(turno_id: int, nuevo_estado_id: int) -> Turno:
        """
        Actualiza el estado de un turno de forma genérica.
        
        Transiciones de estado válidas:
        - RESERVADO (1) → CONFIRMADO (2) o CANCELADO (4)
        - CONFIRMADO (2) → COMPLETADO (3) o CANCELADO (4)
        - COMPLETADO (3) → No permite cambios
        - CANCELADO (4) → No permite cambios
        
        Args:
            turno_id: ID del turno
            nuevo_estado_id: ID del nuevo estado (1-RESERVADO, 2-CONFIRMADO, 3-COMPLETADO, 4-CANCELADO)
            
        Returns:
            Turno actualizado
        """
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        # Obtener el nuevo estado
        nuevo_estado = EstadoTurno.query.filter_by(id=nuevo_estado_id).first()
        if not nuevo_estado:
            raise ValueError(f"Estado con ID {nuevo_estado_id} no encontrado")
        
        estado_actual = turno.estado.nombre
        estado_nuevo = nuevo_estado.nombre
        
        # Validar transiciones de estado permitidas
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
        
        # Actualizar el estado
        turno.estado_id = nuevo_estado_id
        db.session.commit()
        db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turno

    @staticmethod
    def get_booking_by_id(turno_id: int) -> Turno:
        """
        Obtiene un turno por su ID.
        
        Args:
            turno_id: ID del turno
            
        Returns:
            Turno encontrado
        """
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        return turno

    @staticmethod
    def list_bookings_by_user(user_id: int) -> list[Turno]:
        """
        Lista todos los turnos creados por un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de turnos
        """
        # Verificar que el usuario existe
        usuario = Usuario.query.filter_by(id=user_id).first()
        if not usuario:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        
        turnos = Turno.query.filter_by(creado_por=user_id).order_by(Turno.fecha.desc()).all()
        
        # Cargar relaciones
        for turno in turnos:
            db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turnos

    @staticmethod
    def list_bookings_by_vehicle(matricula: str) -> list[Turno]:
        """
        Lista todos los turnos de un vehículo.
        
        Args:
            matricula: Matrícula del vehículo
            
        Returns:
            Lista de turnos
        """
        vehiculo = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehiculo:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        turnos = Turno.query.filter_by(vehiculo_id=vehiculo.id).order_by(Turno.fecha.desc()).all()
        
        # Cargar relaciones
        for turno in turnos:
            db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turnos

    @staticmethod
    def list_all_bookings() -> list[Turno]:
        """
        Lista todos los turnos del sistema.
        
        Returns:
            Lista de turnos
        """
        turnos = Turno.query.order_by(Turno.fecha.desc()).all()
        
        # Cargar relaciones
        for turno in turnos:
            db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turnos

