from src import db

class ResultadoInspeccion(db.Model):
    __tablename__ = "resultado_inspeccion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    inspecciones = db.relationship("Inspeccion", back_populates="resultado")
