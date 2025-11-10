from src.services.user_service import UserService
from src.schemas.user_schemas import UserRegisterRequest, UserResponse, UserLoginRequest, UserLoginResponse
from src.utils.jwt_utils import generate_token
from flask import request, jsonify
from pydantic import ValidationError


def register_user():
    try:
        data = UserRegisterRequest(**request.json)
        user = UserService.create_user(data.model_dump())

        response_data = {
            "id": user.id,
            "nombre_completo": user.nombre_completo,
            "mail": user.mail,
            "telefono": user.telefono,
            "rol": user.rol.nombre,  # Accede al nombre del rol desde la relación
            "activo": user.activo
        }
        
        response = UserResponse(**response_data)
        return jsonify(response.model_dump()), 201
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def login_user():
    try:
        data = UserLoginRequest(**request.json)
        user = UserService.login_user(data.model_dump())
        
        token = generate_token(user.id, user.mail, user.rol.nombre)
        
        response_data = {
            "id": user.id,
            "nombre_completo": user.nombre_completo,
            "mail": user.mail,
            "telefono": user.telefono,
            "rol": user.rol.nombre, 
            "activo": user.activo,
            "token": token
        }
        
        response = UserLoginResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_user_profile(user_id):
    try:
        user = UserService.get_user_profile(user_id)

        response_data = {
            "id": user.id,
            "nombre_completo": user.nombre_completo,
            "mail": user.mail,
            "telefono": user.telefono,
            "rol": user.rol.nombre, 
            "activo": user.activo
        }
        
        response = UserResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except ValidationError:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400
