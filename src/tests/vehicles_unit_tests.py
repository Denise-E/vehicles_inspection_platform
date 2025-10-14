import pytest
import os
from src import create_app, db
from src.models import Vehiculo, EstadoVehiculo, Usuario, UsuarioRol
from src.utils.hash_utils import hash_password


@pytest.fixture
def app():
    """Crea y configura la aplicación para testing"""
    # Guardar la URL original de la base de datos
    original_db_uri = os.environ.get('DATABASE_URL')
    
    # Configurar la base de datos de prueba ANTES de crear la app
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Verificar si los roles ya existen antes de crearlos
        existing_roles = UsuarioRol.query.all()
        if not existing_roles:
            # Crear roles necesarios para los tests
            admin_rol = UsuarioRol(nombre='ADMIN')
            inspector_rol = UsuarioRol(nombre='INSPECTOR')
            duenio_rol = UsuarioRol(nombre='DUENIO')
            
            db.session.add_all([admin_rol, inspector_rol, duenio_rol])
            db.session.commit()
        
        # Crear estados de vehículos
        existing_states = EstadoVehiculo.query.all()
        if not existing_states:
            activo_estado = EstadoVehiculo(nombre='ACTIVO')
            inactivo_estado = EstadoVehiculo(nombre='INACTIVO')
            
            db.session.add_all([activo_estado, inactivo_estado])
            db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()
    
    # Restaurar la configuración original
    if original_db_uri:
        os.environ['DATABASE_URL'] = original_db_uri


@pytest.fixture
def client(app):
    """Cliente de prueba para realizar peticiones HTTP"""
    return app.test_client()


# ========================================
# TESTS PARA /api/vehicles/register/{duenio_id}
# ========================================

def test_register_vehicle_success(client, app):
    """Test: Registro exitoso de un vehículo"""
    with app.app_context():
        # Crear usuario con rol DUENIO
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Pedro Gomez",
            mail="pedro@example.com",
            telefono="123456789",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Registrar vehículo
        data = {
            "matricula": "ABC123",
            "marca": "Toyota",
            "modelo": "Corolla",
            "anio": 2020
        }
        
        response = client.post(f'/api/vehicles/register/{user_id}', json=data)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['matricula'] == "ABC123"
        assert response_data['marca'] == "Toyota"
        assert response_data['modelo'] == "Corolla"
        assert response_data['anio'] == 2020
        assert response_data['estado'] == "ACTIVO"
        assert 'id' in response_data


def test_register_vehicle_duplicate_matricula(client, app):
    """Test: Registro falla con matrícula ya registrada"""
    with app.app_context():
        # Crear usuario con rol DUENIO
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Maria Lopez",
            mail="maria@example.com",
            telefono="987654321",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Crear vehículo previo
        estado = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        existing_vehicle = Vehiculo(
            matricula="XYZ789",
            marca="Ford",
            modelo="Focus",
            anio=2019,
            duenio_id=user_id,
            estado_id=estado.id
        )
        db.session.add(existing_vehicle)
        db.session.commit()
        
        # Intentar registrar vehículo con la misma matrícula
        data = {
            "matricula": "XYZ789",
            "marca": "Chevrolet",
            "modelo": "Cruze",
            "anio": 2021
        }
        
        response = client.post(f'/api/vehicles/register/{user_id}', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "ya existe" in response_data['error'].lower()


def test_register_vehicle_user_with_admin_role(client, app):
    """Test: Registro falla con usuario rol ADMIN"""
    with app.app_context():
        # Crear usuario con rol ADMIN
        rol = UsuarioRol.query.filter_by(nombre='ADMIN').first()
        user = Usuario(
            nombre_completo="Admin User",
            mail="admin@example.com",
            telefono="111222333",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Intentar registrar vehículo con usuario ADMIN
        data = {
            "matricula": "ADM999",
            "marca": "BMW",
            "modelo": "X5",
            "anio": 2022
        }
        
        response = client.post(f'/api/vehicles/register/{user_id}', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "no puede registrar" in response_data['error'].lower()


def test_register_vehicle_user_with_inspector_role(client, app):
    """Test: Registro falla con usuario rol INSPECTOR"""
    with app.app_context():
        # Crear usuario con rol INSPECTOR
        rol = UsuarioRol.query.filter_by(nombre='INSPECTOR').first()
        user = Usuario(
            nombre_completo="Inspector User",
            mail="inspector@example.com",
            telefono="444555666",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Intentar registrar vehículo con usuario INSPECTOR
        data = {
            "matricula": "INS888",
            "marca": "Mercedes",
            "modelo": "C-Class",
            "anio": 2021
        }
        
        response = client.post(f'/api/vehicles/register/{user_id}', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "no puede registrar" in response_data['error'].lower()

