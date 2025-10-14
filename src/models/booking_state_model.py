from src import db

class EstadoTurno(db.Model):
    __tablename__ = "estado_turno"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    turnos = db.relationship("Turno", back_populates="estado")
