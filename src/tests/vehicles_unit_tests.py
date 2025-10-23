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


# ========================================
# TESTS PARA /api/vehicles/{matricula} (GET - Profile)
# ========================================

def test_get_vehicle_profile_success(client, app):
    """Test: Obtener perfil de vehículo exitosamente"""
    with app.app_context():
        # Crear usuario y vehículo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Carlos Martinez",
            mail="carlos@example.com",
            telefono="333444555",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        estado = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehicle = Vehiculo(
            matricula="GET123",
            marca="Honda",
            modelo="Civic",
            anio=2020,
            duenio_id=user.id,
            estado_id=estado.id
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Obtener perfil
        response = client.get('/api/vehicles/profile/GET123')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['matricula'] == "GET123"
        assert response_data['marca'] == "Honda"
        assert response_data['nombre_duenio'] == "Carlos Martinez"


def test_get_vehicle_profile_not_found(client, app):
    """Test: Obtener perfil falla con vehículo no existente"""
    with app.app_context():
        response = client.get('/api/vehicles/profile/NOEXISTE')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/vehicles (GET - List all)
# ========================================

def test_list_all_vehicles_success(client, app):
    """Test: Listar todos los vehículos exitosamente"""
    with app.app_context():
        # Crear usuarios y vehículos
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user1 = Usuario(
            nombre_completo="Luis Hernandez",
            mail="luis@example.com",
            telefono="666777888",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        user2 = Usuario(
            nombre_completo="Ana Garcia",
            mail="ana@example.com",
            telefono="999000111",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add_all([user1, user2])
        db.session.commit()
        
        estado = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehicle1 = Vehiculo(
            matricula="LST001",
            marca="Nissan",
            modelo="Sentra",
            anio=2019,
            duenio_id=user1.id,
            estado_id=estado.id
        )
        vehicle2 = Vehiculo(
            matricula="LST002",
            marca="Mazda",
            modelo="3",
            anio=2021,
            duenio_id=user2.id,
            estado_id=estado.id
        )
        db.session.add_all([vehicle1, vehicle2])
        db.session.commit()
        
        # Listar vehículos
        response = client.get('/api/vehicles')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'vehiculos' in response_data
        assert 'total' in response_data
        assert response_data['total'] >= 2


# ========================================
# TESTS PARA /api/vehicles/{matricula} (PUT - Update)
# ========================================

def test_update_vehicle_success(client, app):
    """Test: Actualizar vehículo exitosamente"""
    with app.app_context():
        # Crear usuario y vehículo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Roberto Silva",
            mail="roberto@example.com",
            telefono="222333444",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        estado = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehicle = Vehiculo(
            matricula="UPD123",
            marca="Volkswagen",
            modelo="Golf",
            anio=2018,
            duenio_id=user.id,
            estado_id=estado.id
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Actualizar vehículo
        data = {
            "marca": "Volkswagen",
            "modelo": "Jetta",
            "anio": 2020
        }
        
        response = client.put('/api/vehicles/UPD123', json=data)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['matricula'] == "UPD123"
        assert response_data['modelo'] == "Jetta"
        assert response_data['anio'] == 2020


def test_update_vehicle_not_found(client, app):
    """Test: Actualizar vehículo falla con matrícula no existente"""
    with app.app_context():
        data = {
            "marca": "Tesla",
            "modelo": "Model 3",
            "anio": 2023
        }
        
        response = client.put('/api/vehicles/NOEXISTE', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_update_vehicle_invalid_year(client, app):
    """Test: Actualizar vehículo falla con año inválido"""
    with app.app_context():
        # Crear usuario y vehículo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Valeria Torres",
            mail="valeria@example.com",
            telefono="555666777",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        estado = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehicle = Vehiculo(
            matricula="INV456",
            marca="Fiat",
            modelo="Punto",
            anio=2017,
            duenio_id=user.id,
            estado_id=estado.id
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Intentar actualizar con año inválido
        data = {
            "marca": "Fiat",
            "modelo": "500",
            "anio": 1850  # Año inválido
        }
        
        response = client.put('/api/vehicles/INV456', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/vehicles/{matricula}/desactivar (PATCH - Soft delete)
# ========================================

def test_delete_vehicle_success(client, app):
    """Test: Desactivar vehículo exitosamente (soft delete con PATCH)"""
    with app.app_context():
        # Crear usuario y vehículo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Diego Ramirez",
            mail="diego@example.com",
            telefono="777888999",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        estado = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehicle = Vehiculo(
            matricula="DEL789",
            marca="Peugeot",
            modelo="208",
            anio=2019,
            duenio_id=user.id,
            estado_id=estado.id
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Desactivar vehículo con PATCH
        response = client.patch('/api/vehicles/DEL789/desactivar')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['matricula'] == "DEL789"
        assert response_data['estado'] == "INACTIVO"


def test_delete_vehicle_not_found(client, app):
    """Test: Desactivar vehículo falla con matrícula no existente"""
    with app.app_context():
        response = client.patch('/api/vehicles/NOEXISTE/desactivar')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_delete_vehicle_already_inactive(client, app):
    """Test: Desactivar vehículo falla si ya está inactivo"""
    with app.app_context():
        # Crear usuario y vehículo INACTIVO
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Sofia Perez",
            mail="sofia@example.com",
            telefono="888999000",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        estado_inactivo = EstadoVehiculo.query.filter_by(nombre='INACTIVO').first()
        vehicle = Vehiculo(
            matricula="INA999",
            marca="Renault",
            modelo="Clio",
            anio=2016,
            duenio_id=user.id,
            estado_id=estado_inactivo.id
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Intentar desactivar vehículo ya inactivo con PATCH
        response = client.patch('/api/vehicles/INA999/desactivar')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "ya está inactivo" in response_data['error']