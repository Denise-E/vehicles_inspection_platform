from src import db
from src.models import Usuario, UsuarioRol
from src.utils.hash_utils import hash_password, check_password_hash


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
        hashed_password = hash_password(data["contrasenia"])

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


    @staticmethod
    def login_user(data) -> Usuario:
        """
        Inicia sesión de un usuario.
        """
        user = Usuario.query.filter_by(mail=data["mail"]).first()

        if not user or not user.activo:
            raise ValueError("Usuario no encontrado")

        if not check_password_hash(user.hash_password, data["contrasenia"]):
            raise ValueError("Contraseña incorrecta")

        # Carga la relación del rol para poder acceder al nombre
        db.session.refresh(user, ['rol'])
        
        return user