from src import db
from src.models import Usuario
from werkzeug.security import generate_password_hash


class UserService:

    @staticmethod
    def create_user(data) -> Usuario:
        """
        Crea un nuevo usuario en la base de datos.
        """
        hashed_password = generate_password_hash(data["password"])

        new_user = Usuario(
            nombre_completo=data["nombre_completo"],
            mail=data["mail"],
            telefono=data.get("telefono"),
            hash_password=hashed_password,
            rol_id=data["rol_id"],
            activo=True
        )

        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)

        return new_user
