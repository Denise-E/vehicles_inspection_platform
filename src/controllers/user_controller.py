from src.services.user_service import UserService
from src.schemas.user_schema import UserRegisterRequest, UserResponse
from flask import request, jsonify


def register_user():
    try:
        # Valida request body con Pydantic
        data = UserRegisterRequest(**request.json)

        # Crea usuario en la base de datos
        user = UserService.create_user(data.dict())

        # Convierte a esquema de respuesta
        response = UserResponse.from_orm(user)
        return jsonify(response.dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
