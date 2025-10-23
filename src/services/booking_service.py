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
    def consultar_disponibilidad(matricula: str, fecha_inicio: Optional[str] = None) -> dict:
        """
        Consulta los slots disponibles para un vehículo en los próximos días.
        
        Args:
            matricula: Matrícula del vehículo
            fecha_inicio: Fecha desde la cual buscar (formato YYYY-MM-DD)
        
        Returns:
            dict con slots disponibles
        """
        # Verificar que el vehículo existe
        vehiculo = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehiculo:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        # Determinar fecha de inicio
        if fecha_inicio:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        else:
            inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Generar slots disponibles
        slots = []
        fecha_actual = inicio
        dias_generados = 0
        
        while dias_generados < HORARIO_CONFIG["dias_anticipacion"]:
            # Solo días laborables (lunes a viernes)
            if fecha_actual.weekday() in HORARIO_CONFIG["dias_laborables"]:
                # Generar slots por hora
                for hora in range(HORARIO_CONFIG["hora_inicio"], HORARIO_CONFIG["hora_fin"]):
                    slot_datetime = fecha_actual.replace(hour=hora, minute=0, second=0, microsecond=0)
                    
                    # Solo mostrar slots futuros
                    if slot_datetime > datetime.now():
                        # Verificar si hay un turno confirmado o reservado en ese horario
                        turno_existente = Turno.query.filter(
                            Turno.vehiculo_id == vehiculo.id,
                            Turno.fecha == slot_datetime,
                            Turno.estado_id.in_([1, 2])  # RESERVADO=1 o CONFIRMADO=2
                        ).first()
                        
                        slots.append({
                            "fecha": slot_datetime.strftime('%Y-%m-%d %H:%M'),
                            "disponible": turno_existente is None
                        })
                
                dias_generados += 1
            
            fecha_actual += timedelta(days=1)
        
        return {
            "matricula": matricula,
            "slots": slots,
            "total_disponibles": sum(1 for slot in slots if slot["disponible"])
        }

    @staticmethod
    def create_booking(data: dict) -> Turno:
        """
        Crea un nuevo turno (estado RESERVADO).
        
        Args:
            data: dict con matricula, fecha, creado_por
            
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
    def confirmar_booking(turno_id: int) -> Turno:
        """
        Confirma un turno (cambia estado a CONFIRMADO).
        
        Args:
            turno_id: ID del turno
            
        Returns:
            Turno confirmado
        """
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        # Solo se puede confirmar un turno en estado RESERVADO
        if turno.estado.nombre != "RESERVADO":
            raise ValueError(f"Solo se pueden confirmar turnos en estado RESERVADO. Estado actual: {turno.estado.nombre}")
        
        # Obtener estado CONFIRMADO (id=2)
        estado_confirmado = EstadoTurno.query.filter_by(nombre="CONFIRMADO").first()
        if not estado_confirmado:
            raise ValueError("Estado CONFIRMADO no encontrado en la base de datos")
        
        turno.estado_id = estado_confirmado.id
        db.session.commit()
        db.session.refresh(turno, ['vehiculo', 'estado', 'creador'])
        
        return turno

    @staticmethod
    def cancelar_booking(turno_id: int) -> Turno:
        """
        Cancela un turno (cambia estado a CANCELADO).
        
        Args:
            turno_id: ID del turno
            
        Returns:
            Turno cancelado
        """
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        # Solo se pueden cancelar turnos RESERVADO o CONFIRMADO
        if turno.estado.nombre not in ["RESERVADO", "CONFIRMADO"]:
            raise ValueError(f"No se puede cancelar un turno en estado {turno.estado.nombre}")
        
        # Obtener estado CANCELADO (id=4)
        estado_cancelado = EstadoTurno.query.filter_by(nombre="CANCELADO").first()
        if not estado_cancelado:
            raise ValueError("Estado CANCELADO no encontrado en la base de datos")
        
        turno.estado_id = estado_cancelado.id
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

