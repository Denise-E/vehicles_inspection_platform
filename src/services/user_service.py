from src import db
from src.models import Usuario, UsuarioRol
from werkzeug.security import generate_password_hash


class UserService:

    @staticmethod
    def create_user(data) -> Usuario:
        """
        Crea un nuevo usuario en la base de datos.
        """
        rol_nombre = data["rol"].upper()
        rol = UsuarioRol.query.filter_by(nombre=rol_nombre).first()
        
        if not rol:
            raise ValueError(f"Rol '{rol_nombre}' no encontrado en la base de datos")
        
        # Hasheo de la contraseña
        hashed_password = generate_password_hash(data["contrasenia"])

        new_user = Usuario(
            nombre_completo=data["nombre_completo"],
            mail=data["mail"],
            telefono=data.get("telefono"),
            hash_password=hashed_password,
            rol_id=rol.id,
            activo=True
        )

        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)
        
        # Carga la relación del rol para poder acceder al nombre
        db.session.refresh(new_user, ['rol'])

        return new_user
