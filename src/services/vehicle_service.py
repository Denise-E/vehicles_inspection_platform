from src import db
from src.models import Vehiculo, Usuario


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

        # Verificar si el vehículo ya existe
        vehicle = Vehiculo.query.filter_by(matricula=data["matricula"]).first()
        if vehicle:
            raise ValueError("El vehículo ya existe")

        vehicle = Vehiculo(
            matricula=data["matricula"],
            marca=data["marca"],
            modelo=data["modelo"],
            anio=data["anio"],
            duenio_id=duenio_id,
            estado_id=1 # ACTIVO
        )

        db.session.add(vehicle)
        db.session.commit()
        db.session.refresh(vehicle, ['estado'])

        return vehicle