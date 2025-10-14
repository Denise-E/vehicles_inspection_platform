from werkzeug.security import generate_password_hash as werkzeug_generate_hash, check_password_hash as werkzeug_check_hash


def hash_password(password: str) -> str:
    """
    Genera un hash de la contraseña usando el algoritmo por defecto de Werkzeug.
    
    Args:
        password (str): La contraseña en texto plano
        
    Returns:
        str: El hash de la contraseña
    """
    return werkzeug_generate_hash(password)


def check_password_hash(hashed_password: str, password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        hashed_password (str): El hash almacenado en la base de datos
        password (str): La contraseña en texto plano a verificar
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    return werkzeug_check_hash(hashed_password, password)
