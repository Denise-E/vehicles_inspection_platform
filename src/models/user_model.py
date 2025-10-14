from src import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    hash_password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("usuario_rol.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    rol = db.relationship("UsuarioRol", back_populates="usuarios")
    vehiculos = db.relationship("Vehiculo", back_populates="duenio", cascade="all, delete-orphan")
    inspecciones = db.relationship("Inspeccion", back_populates="inspector")
