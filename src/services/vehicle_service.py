from src import db
from src.models import Vehiculo, Usuario, EstadoVehiculo


class VehicleService:

    @staticmethod
    def create_vehicle(data: dict, duenio_id: int) -> Vehiculo:
        """
        Crea un nuevo vehículo en la base de datos.
        """
        # Verificar usuario tenga rol DUENIO
        user = Usuario.query.filter_by(id=duenio_id).first()
        if not user or user.rol.nombre != "DUENIO":
            raise ValueError("El usuario no puede registrar un vehículo")

        vehicle = Vehiculo.query.filter_by(matricula=data["matricula"]).first()
        if vehicle:
            raise ValueError("El vehículo ya existe")

        vehicle = Vehiculo(
            matricula=data["matricula"],
            marca=data["marca"],
            modelo=data["modelo"],
            anio=data["anio"],
            duenio_id=duenio_id,
            estado_id=1  # Activo
        )

        db.session.add(vehicle)
        db.session.commit()
        db.session.refresh(vehicle, ['estado'])

        return vehicle

    @staticmethod
    def get_vehicle_by_matricula(matricula: str, user_id: int = None, user_role: str = None) -> Vehiculo:
        """
        Obtiene un vehículo por su matrícula.
        - ADMIN e INSPECTOR: pueden ver cualquier vehículo
        - DUENIO: solo puede ver sus propios vehículos
        """
        vehicle = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehicle:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        if user_role and user_role not in ["ADMIN", "INSPECTOR"]:
            if vehicle.duenio_id != user_id:
                raise ValueError("No tiene permisos para ver este vehículo")
        
        db.session.refresh(vehicle, ['estado', 'duenio'])
        return vehicle

    @staticmethod
    def list_all_vehicles(user_id: int = None, user_role: str = None) -> list[Vehiculo]:
        """
        Lista vehículos del sistema.
        - ADMIN: ve todos los vehículos
        - DUENIO: solo ve sus propios vehículos
        """
        if user_role == "ADMIN" or user_role == "INSPECTOR":
            vehicles = Vehiculo.query.all()
        else:
            vehicles = Vehiculo.query.filter_by(duenio_id=user_id).all()
        
        for vehicle in vehicles:
            db.session.refresh(vehicle, ['estado', 'duenio'])
        
        return vehicles

    @staticmethod
    def update_vehicle(matricula: str, data: dict, user_id: int = None, user_role: str = None) -> Vehiculo:
        """
        Actualiza un vehículo existente.
        - ADMIN puede actualizar cualquier vehículo
        - DUENIO solo puede actualizar sus propios vehículos
        """
        vehicle = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehicle:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        if vehicle.estado_id == 2: # Estado 2 = INACTIVO
            raise ValueError("No se puede actualizar un vehículo INACTIVO")
        
        if user_role and user_role != 'ADMIN':
            if vehicle.duenio_id != user_id:
                raise ValueError("No tienes permiso para actualizar este vehículo")
        
        vehicle.marca = data.get("marca", vehicle.marca)
        vehicle.modelo = data.get("modelo", vehicle.modelo)
        vehicle.anio = data.get("anio", vehicle.anio)
        
        db.session.commit()
        db.session.refresh(vehicle, ['estado', 'duenio'])
        
        return vehicle

    @staticmethod
    def delete_vehicle(matricula: str) -> Vehiculo:
        """
        Elimina un vehículo (soft delete - cambia estado a INACTIVO).
        """
        vehicle = Vehiculo.query.filter_by(matricula=matricula).first()
        if not vehicle:
            raise ValueError(f"Vehículo con matrícula {matricula} no encontrado")
        
        if vehicle.estado.nombre == "INACTIVO":
            raise ValueError(f"El vehículo con matrícula {matricula} ya está inactivo")
        
        estado_inactivo = EstadoVehiculo.query.filter_by(nombre="INACTIVO").first()
        if not estado_inactivo:
            raise ValueError("Estado INACTIVO no encontrado en la base de datos")
        
        vehicle.estado_id = estado_inactivo.id
        db.session.commit()
        db.session.refresh(vehicle, ['estado', 'duenio'])
        
        return vehicle
        