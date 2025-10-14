from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

"""
Application Factory Pattern— es el estándar recomendado por Flask en proyectos medianos o grandes.

- La idea es que la aplicación se pueda crear y configurar en un solo lugar, y luego se pueda usar en cualquier lugar.
- Se crea una función que se encarga de crear y configurar la aplicación.
- Permite crear la app desde fuera sin dependencias circulares.

"""
def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Configuración base
    # La utiliza internamente Flask para firmar y proteger datos sensibles (cookies, tokens, etc.)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # Configuración de CORS para permitir peticiones desde cualquier origen. Configuración lista para su uso a futuro. 
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Routers
    from src.routes.user_router import users
    from src.routes.vehicles_router import vehicles
    from src.routes.bookings_router import bookings
    from src.routes.inspection_router import inspections

    # Register blueprints - routes files connection
    app.register_blueprint(users, url_prefix="/api/users")
    app.register_blueprint(vehicles, url_prefix="/api/vehicles")
    app.register_blueprint(bookings, url_prefix="/api/bookings")
    app.register_blueprint(inspections, url_prefix="/api/inspections")

    # Health check
    @app.route("/api/health", methods=['GET'])
    def health():
        return {"msg": "App running!"}, 200

    return app
