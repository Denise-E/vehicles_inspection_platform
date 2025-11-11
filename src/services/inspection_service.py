from src import db
from src.models import (
    Inspeccion, 
    Chequeo, 
    Turno, 
    EstadoTurno, 
    Vehiculo, 
    EstadoVehiculo,
    ResultadoInspeccion,
    Usuario
)
from datetime import datetime


class InspectionService:
    
    @staticmethod
    def create_inspection(data: dict) -> Inspeccion:
        """
        Crea una inspección completa
        
        Validaciones:
        - El turno debe existir
        - El turno debe estar en estado CONFIRMADO
        - El turno no debe tener ya una inspección
        - El inspector debe existir y tener rol INSPECTOR
        - Debe proporcionar los 8 chequeos
        
        Reglas de negocio:
        - SEGURO: suma >= 80 Y ningún chequeo < 5
        - RECHEQUEAR: suma < 40 O algún chequeo < 5 (observación OBLIGATORIA)
        - Rango intermedio (40-79): también RECHEQUEAR (observación OBLIGATORIA)
        """
        turno_id = data["turno_id"]
        inspector_id = data["inspector_id"]
        chequeos_data = data["chequeos"]
        observacion = data.get("observacion")
        
        # Verificar que el turno existe
        turno = Turno.query.filter_by(id=turno_id).first()
        if not turno:
            raise ValueError(f"Turno con ID {turno_id} no encontrado")
        
        # Verificar que el turno está CONFIRMADO
        estado_confirmado = EstadoTurno.query.filter_by(nombre='CONFIRMADO').first()
        if turno.estado_id != estado_confirmado.id:
            raise ValueError("Solo se pueden crear inspecciones para turnos confirmados")
        
        # Verificar que el turno no tiene ya una inspección
        existing_inspection = Inspeccion.query.filter_by(turno_id=turno_id).first()
        if existing_inspection:
            raise ValueError(f"El turno {turno_id} ya tiene una inspección asociada")
        
        # Verificar que el inspector existe y tiene rol INSPECTOR
        inspector = Usuario.query.filter_by(id=inspector_id).first()
        if not inspector:
            raise ValueError(f"Inspector con ID {inspector_id} no encontrado")
        
        db.session.refresh(inspector, ['rol'])
        if inspector.rol.nombre != 'INSPECTOR':
            raise ValueError(f"El usuario {inspector_id} no tiene rol INSPECTOR")
        
        if len(chequeos_data) != 8:
            raise ValueError("Debe proporcionar la totalidad de los chequeos")
        
        vehiculo = turno.vehiculo
        
        # Calcular puntuación total y determinar resultado
        puntuaciones = [chequeo["puntuacion"] for chequeo in chequeos_data]
        puntuacion_total = sum(puntuaciones)
        minimo_chequeo = min(puntuaciones)
        
        # Determinar resultado según reglas de negocio
        if puntuacion_total >= 80 and minimo_chequeo >= 5:
            resultado_nombre = "SEGURO"
            estado_vehiculo_nombre = "ACTIVO"
        elif puntuacion_total < 40 or minimo_chequeo < 5:
            resultado_nombre = "RECHEQUEAR"
            estado_vehiculo_nombre = "RECHEQUEAR"
            
            # Validar observación obligatoria
            if not observacion or len(observacion.strip()) < 10:
                raise ValueError(
                    "Para un resultado RECHEQUEAR es obligatorio proporcionar una observación "
                    "detallada (mínimo 10 caracteres) explicando los problemas detectados"
                )
        else:
            # Caso intermedio: 40 <= puntuacion <= 79 con todos los chequeos >= 5
            resultado_nombre = "RECHEQUEAR"
            estado_vehiculo_nombre = "RECHEQUEAR"
            
            if not observacion or len(observacion.strip()) < 10:
                raise ValueError(
                    "Para un resultado RECHEQUEAR es obligatorio proporcionar una observación "
                    "detallada (mínimo 10 caracteres) explicando los problemas detectados"
                )
        
        # Obtener resultado de inspección
        resultado = ResultadoInspeccion.query.filter_by(nombre=resultado_nombre).first()
        if not resultado:
            raise ValueError(f"Resultado '{resultado_nombre}' no encontrado en la base de datos")
        
        # Obtener estado de vehículo
        estado_vehiculo = EstadoVehiculo.query.filter_by(nombre=estado_vehiculo_nombre).first()
        if not estado_vehiculo:
            raise ValueError(f"Estado '{estado_vehiculo_nombre}' no encontrado en la base de datos")
        
        new_inspection = Inspeccion(
            vehiculo_id=vehiculo.id,
            turno_id=turno_id,
            inspector_id=inspector_id,
            fecha=datetime.utcnow(),
            puntuacion_total=puntuacion_total,
            resultado_id=resultado.id,
            observacion=observacion
        )
        
        db.session.add(new_inspection)
        db.session.flush() 
        
        for chequeo_data in chequeos_data:
            chequeo = Chequeo(
                inspeccion_id=new_inspection.id,
                descripcion=chequeo_data["descripcion"],
                puntuacion=chequeo_data["puntuacion"],
                fecha=datetime.utcnow()
            )
            db.session.add(chequeo)
        
        vehiculo.estado_id = estado_vehiculo.id
        
        estado_turno_completado = EstadoTurno.query.filter_by(nombre='COMPLETADO').first()
        if estado_turno_completado:
            turno.estado_id = estado_turno_completado.id
        
        db.session.commit()
        db.session.refresh(new_inspection, ['chequeos', 'vehiculo', 'inspector', 'turno', 'resultado'])
        
        return new_inspection
    
    @staticmethod
    def get_inspection_by_id(inspeccion_id: int, user_id: int = None, user_role: str = None) -> Inspeccion:
        """
        Obtiene una inspección por su ID con todos sus chequeos.
        
        Validaciones de autorización:
        - ADMIN e INSPECTOR pueden ver cualquier inspección
        - DUENIO solo puede ver inspecciones de sus propios vehículos
        """
        inspeccion = Inspeccion.query.filter_by(id=inspeccion_id).first()
        if not inspeccion:
            raise ValueError(f"Inspección con ID {inspeccion_id} no encontrada")
        
        db.session.refresh(inspeccion, ['chequeos', 'vehiculo', 'inspector', 'turno', 'resultado'])
        
        # Validar autorización por rol
        if user_role not in ['ADMIN', 'INSPECTOR']:
            # Si es DUENIO, verificar que el vehículo le pertenece
            if inspeccion.vehiculo.duenio_id != user_id:
                raise ValueError("No tienes permiso para ver esta inspección. Solo puedes ver inspecciones de tus propios vehículos")
        
        return inspeccion
    
    @staticmethod
    def list_inspections_by_vehiculo(matricula: str, user_id: int = None, user_role: str = None) -> list[Inspeccion]:
        """
        Lista todas las inspecciones de un vehículo por matrícula.
        
        Validaciones de autorización:
        - ADMIN e INSPECTOR pueden ver inspecciones de cualquier vehículo
        - DUENIO solo puede ver inspecciones de sus propios vehículos
        """
        vehiculo = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehiculo:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        # Validar autorización por rol
        if user_role not in ['ADMIN', 'INSPECTOR']:
            # Si es DUENIO, verificar que el vehículo le pertenece
            if vehiculo.duenio_id != user_id:
                raise ValueError("No tienes permiso para ver inspecciones de este vehículo. Solo puedes ver inspecciones de tus propios vehículos")
        
        inspecciones = Inspeccion.query.filter_by(vehiculo_id=vehiculo.id).all()
        
        for inspeccion in inspecciones:
            db.session.refresh(inspeccion, ['vehiculo', 'inspector', 'resultado'])
        
        return inspecciones
    
    @staticmethod
    def list_inspections_by_inspector(inspector_id: int, user_id: int = None, user_role: str = None) -> list[Inspeccion]:
        """
        Lista todas las inspecciones realizadas por un inspector.
        
        Validaciones de autorización:
        - ADMIN puede ver inspecciones de cualquier inspector
        - INSPECTOR solo puede ver sus propias inspecciones
        """
        # Validar autorización por rol
        if user_role != 'ADMIN':
            # Si es INSPECTOR, verificar que está consultando sus propias inspecciones
            if inspector_id != user_id:
                raise ValueError("No tienes permiso para ver inspecciones de otro inspector. Solo puedes ver tus propias inspecciones")
        
        inspector = Usuario.query.filter_by(id=inspector_id).first()
        if not inspector:
            raise ValueError(f"Inspector con ID {inspector_id} no encontrado")
        
        inspecciones = Inspeccion.query.filter_by(inspector_id=inspector_id).all()
        
        for inspeccion in inspecciones:
            db.session.refresh(inspeccion, ['vehiculo', 'inspector', 'resultado'])
        
        return inspecciones
    
    @staticmethod
    def list_all_inspections() -> list[Inspeccion]:
        """
        Lista todas las inspecciones del sistema.
        """
        inspecciones = Inspeccion.query.all()
        
        for inspeccion in inspecciones:
            db.session.refresh(inspeccion, ['vehiculo', 'inspector', 'resultado'])
        
        return inspecciones

