from datetime import datetime
from src import db


class Chequeo(db.Model):
    __tablename__ = "chequeo"

    id = db.Column(db.Integer, primary_key=True)
    inspeccion_id = db.Column(db.Integer, db.ForeignKey("inspeccion.id"))
    descripcion = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    puntuacion = db.Column(db.Integer, nullable=False)

    inspeccion = db.relationship("Inspeccion", back_populates="chequeos")
