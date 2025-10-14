from datetime import datetime
from src import db


class Turno(db.Model):
    __tablename__ = "turno"

    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculo.id"), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado_id = db.Column(db.Integer, db.ForeignKey("estado_turno.id"), nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    vehiculo = db.relationship("Vehiculo", back_populates="turnos")
    estado = db.relationship("EstadoTurno", back_populates="turnos")
    creador = db.relationship("Usuario")
    inspeccion = db.relationship("Inspeccion", back_populates="turno", uselist=False)
