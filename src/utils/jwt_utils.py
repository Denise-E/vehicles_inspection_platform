import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify


def generate_token(user_id: int, user_email: str, user_role: str) -> str:
    """
    Genera un JWT token para un usuario.
    
    Args:
        user_id: ID del usuario
        user_email: Email del usuario
        user_role: Rol del usuario (DUENIO, INSPECTOR, ADMIN)
        
    Returns:
        Token JWT como string
    """
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY no está configurada en las variables de entorno")
    
    # Payload del token
    payload = {
        'user_id': user_id,
        'email': user_email,
        'role': user_role,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token válido por 24 horas
        'iat': datetime.utcnow()  # Issued at
    }
    
    # Generar token
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un JWT token.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Payload decodificado si el token es válido, None en caso contrario
    """
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY no está configurada en las variables de entorno")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido


def token_required(f):
    """
    Decorador para proteger endpoints que requieren autenticación.
    Verifica que exista un Bearer Token válido en el header Authorization.
    
    Usage:
        @token_required
        def protected_endpoint():
            # current_user estará disponible en el contexto
            return {"msg": "Success"}
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                # Formato esperado: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Formato de token inválido. Use 'Bearer <token>'"}), 401
        
        if not token:
            return jsonify({"error": "Token no proporcionado. Se requiere autenticación"}), 401
        
        # Verificar token
        payload = verify_token(token)
        
        if payload is None:
            return jsonify({"error": "Token inválido o expirado"}), 401
        
        # Agregar información del usuario al contexto de la request
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(*allowed_roles):
    """
    Decorador para proteger endpoints por rol de usuario.
    Debe usarse junto con @token_required.
    
    Args:
        allowed_roles: Roles permitidos (DUENIO, INSPECTOR, ADMIN)
        
    Usage:
        @token_required
        @role_required('ADMIN', 'INSPECTOR')
        def admin_only_endpoint():
            return {"msg": "Success"}
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Verificar que haya un usuario autenticado
            if not hasattr(request, 'current_user'):
                return jsonify({"error": "Se requiere autenticación"}), 401
            
            user_role = request.current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    "error": f"Acceso denegado. Se requiere uno de estos roles: {', '.join(allowed_roles)}"
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

