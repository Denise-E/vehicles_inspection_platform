from src import db


class Vehiculo(db.Model):
    __tablename__ = "vehiculo"

    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    duenio_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey("estado_vehiculo.id"), nullable=False)

    duenio = db.relationship("Usuario", back_populates="vehiculos")
    estado = db.relationship("EstadoVehiculo", back_populates="vehiculos")
    turnos = db.relationship("Turno", back_populates="vehiculo", cascade="all, delete-orphan")
    inspecciones = db.relationship("Inspeccion", back_populates="vehiculo")
