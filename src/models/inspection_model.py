from datetime import datetime
from src import db


class Inspeccion(db.Model):
    __tablename__ = "inspeccion"

    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculo.id"), nullable=False)
    turno_id = db.Column(db.Integer, db.ForeignKey("turno.id"), unique=True)
    inspector_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    puntuacion_total = db.Column(db.Integer, default=0)
    resultado_id = db.Column(db.Integer, db.ForeignKey("resultado_inspeccion.id"))
    observacion = db.Column(db.Text)

    vehiculo = db.relationship("Vehiculo", back_populates="inspecciones")
    turno = db.relationship("Turno", back_populates="inspeccion")
    inspector = db.relationship("Usuario", back_populates="inspecciones")
    resultado = db.relationship("ResultadoInspeccion", back_populates="inspecciones")
    chequeos = db.relationship("Chequeo", back_populates="inspeccion", cascade="all, delete-orphan")
