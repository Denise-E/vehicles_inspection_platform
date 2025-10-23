from src.services.user_service import UserService
from src.schemas.user_schemas import UserRegisterRequest, UserResponse, UserLoginRequest, UserLoginResponse
from src.utils.jwt_utils import generate_token
from flask import request, jsonify


def register_user():
    try:
        # Valida request body con Pydantic
        data = UserRegisterRequest(**request.json)

        # Crea usuario en la base de datos
        user = UserService.create_user(data.model_dump())

        response_data = {
            "id": user.id,
            "nombre_completo": user.nombre_completo,
            "mail": user.mail,
            "telefono": user.telefono,
            "rol": user.rol.nombre,  # Accede al nombre del rol desde la relación
            "activo": user.activo
        }
        
        # Valida response body con Pydantic
        response = UserResponse(**response_data)
        return jsonify(response.model_dump()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def login_user():
    try:
        # Valida request body con Pydantic
        data = UserLoginRequest(**request.json)
        
        user = UserService.login_user(data.model_dump())
        
        # Generar token JWT
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
        
        # Valida response body con Pydantic (ahora incluye token)
        response = UserLoginResponse(**response_data)
        return jsonify(response.model_dump()), 200
        
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
        
        # Valida response body con Pydantic
        response = UserResponse(**response_data)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
