from src import db

class UsuarioRol(db.Model):
    __tablename__ = "usuario_rol"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", back_populates="rol")
