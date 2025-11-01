from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_swagger import swagger
import os

"""
Application Factory Pattern— es el estándar recomendado por Flask en proyectos medianos o grandes.

- La idea es que la aplicación se pueda crear y configurar en un solo lugar, y luego se pueda usar en cualquier lugar.
- Se crea una función que se encarga de crear y configurar la aplicación.
- Permite crear la app desde fuera sin dependencias circulares.

"""

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    # Configurar template_folder para que apunte a la raíz del proyecto
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    
    app = Flask(__name__, template_folder=template_dir)
    load_dotenv()

    # Configuración base
    # La utiliza internamente Flask para firmar y proteger datos sensibles (cookies, tokens, etc.)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # Configuración de CORS para permitir peticiones desde cualquier origen. Configuración lista para su uso a futuro. 
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)

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
        """
        Health check endpoint
        ---
        tags:
          - Health
        responses:
          200:
            description: API está funcionando correctamente
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: App running!
        """
        return {"msg": "App running!"}, 200

    # Swagger endpoint - JSON spec
    @app.route("/swagger")
    def swagger_spec():
        """
        Genera la especificación Swagger/OpenAPI de la API en formato JSON
        """
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "Vehicle Inspection Platform API"
        swag['info']['description'] = "API para sistema de control de inspección vehicular - Proyecto universitario TAP 2025"
        swag['host'] = "localhost:5000"
        swag['basePath'] = "/"
        swag['schemes'] = ["http"]
        
        # Configuración de seguridad JWT
        swag['securityDefinitions'] = {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Bearer token. Formato: "Bearer {token}"'
            }
        }
        
        return jsonify(swag)

    # Swagger UI - Interfaz visual
    @app.route("/docs")
    def swagger_ui():
        """
        Interfaz visual de Swagger UI para explorar y probar la API
        """
        return render_template('swagger.html')

    return app
