import pytest
import os
from datetime import datetime, timedelta
from src import create_app, db
from src.models import (
    Usuario, UsuarioRol, Vehiculo, EstadoVehiculo, 
    Turno, EstadoTurno, ResultadoInspeccion
)
from src.utils.hash_utils import hash_password


@pytest.fixture
def app():
    """Crea y configura la aplicación para testing"""
    original_db_uri = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Crear roles
        if not UsuarioRol.query.all():
            admin_rol = UsuarioRol(nombre='ADMIN')
            inspector_rol = UsuarioRol(nombre='INSPECTOR')
            duenio_rol = UsuarioRol(nombre='DUENIO')
            db.session.add_all([admin_rol, inspector_rol, duenio_rol])
            db.session.commit()
        
        # Crear estados de vehículo
        if not EstadoVehiculo.query.all():
            activo = EstadoVehiculo(nombre='ACTIVO')
            inactivo = EstadoVehiculo(nombre='INACTIVO')
            db.session.add_all([activo, inactivo])
            db.session.commit()
        
        # Crear estados de turno
        if not EstadoTurno.query.all():
            reservado = EstadoTurno(nombre='RESERVADO')
            confirmado = EstadoTurno(nombre='CONFIRMADO')
            completado = EstadoTurno(nombre='COMPLETADO')
            cancelado = EstadoTurno(nombre='CANCELADO')
            db.session.add_all([reservado, confirmado, completado, cancelado])
            db.session.commit()
        
        # Crear resultados de inspección
        if not ResultadoInspeccion.query.all():
            seguro = ResultadoInspeccion(nombre='SEGURO')
            rechequear_res = ResultadoInspeccion(nombre='RECHEQUEAR')
            db.session.add_all([seguro, rechequear_res])
            db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()
    
    if original_db_uri:
        os.environ['DATABASE_URL'] = original_db_uri


@pytest.fixture
def client(app):
    """Cliente de prueba para realizar peticiones HTTP"""
    return app.test_client()


def get_auth_token(client, app, mail="test_inspect@example.com", password="password123", role="INSPECTOR"):
    """
    Helper function para obtener un token JWT.
    """
    with app.app_context():
        rol = UsuarioRol.query.filter_by(nombre=role).first()
        existing_user = Usuario.query.filter_by(mail=mail).first()
        
        if not existing_user:
            user = Usuario(
                nombre_completo="Test Inspector User",
                mail=mail,
                telefono="123456789",
                hash_password=hash_password(password),
                rol_id=rol.id,
                activo=True
            )
            db.session.add(user)
            db.session.commit()
        
        login_data = {
            "mail": mail,
            "contrasenia": password
        }
        response = client.post('/api/users/sessions', json=login_data)
        return response.get_json()['token']


@pytest.fixture
def setup_data(app):
    """Crea datos de prueba (inspector, dueño, vehículo, turno)"""
    with app.app_context():
        # Crear inspector
        rol_inspector = UsuarioRol.query.filter_by(nombre='INSPECTOR').first()
        inspector = Usuario(
            nombre_completo="Inspector Prueba",
            mail="inspector_test@example.com",
            telefono="987654321",
            hash_password=hash_password("password123"),
            rol_id=rol_inspector.id,
            activo=True
        )
        db.session.add(inspector)
        
        # Crear dueño
        rol_duenio = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        duenio = Usuario(
            nombre_completo="Dueño Prueba",
            mail="duenio_test@example.com",
            telefono="111222333",
            hash_password=hash_password("password123"),
            rol_id=rol_duenio.id,
            activo=True
        )
        db.session.add(duenio)
        db.session.commit()
        
        # Crear vehículo
        estado_activo = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehiculo = Vehiculo(
            matricula="TEST123",
            marca="TestMarca",
            modelo="TestModelo",
            anio=2020,
            duenio_id=duenio.id,
            estado_id=estado_activo.id
        )
        db.session.add(vehiculo)
        db.session.commit()
        
        # Crear turno CONFIRMADO para HOY
        fecha_turno = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        
        estado_confirmado = EstadoTurno.query.filter_by(nombre='CONFIRMADO').first()
        turno = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_confirmado.id,
            creado_por=duenio.id
        )
        db.session.add(turno)
        db.session.commit()
        
        return {
            "inspector_id": inspector.id,
            "duenio_id": duenio.id,
            "vehiculo_id": vehiculo.id,
            "turno_id": turno.id,
            "matricula": vehiculo.matricula
        }


# ========================================
# TESTS PARA /api/inspections (POST - Crear inspección)
# ========================================

def test_create_inspection_resultado_seguro(client, app, setup_data):
    """Test: Crear inspección con resultado SEGURO (40 ≤ suma ≤ 80 y todos >= 5)"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Chequeos totalizando 80 puntos (nota máxima), todos >= 5 -> resultado SEGURO
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 10},
                {"descripcion": "Frenos", "puntuacion": 10},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 10},
                {"descripcion": "Chasis y estructura", "puntuacion": 10},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 10},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 10}
            ],
            "observacion": "Vehículo en excelentes condiciones"
        }
        
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['turno_id'] == setup_data["turno_id"]
        assert response_data['vehiculo_matricula'] == setup_data["matricula"]
        assert response_data['resultado'] == 'SEGURO'
        assert response_data['puntuacion_total'] == 80
        assert 'id' in response_data
        assert 'chequeos' in response_data
        assert len(response_data['chequeos']) == 8


def test_create_inspection_without_inspector_role(client, app, setup_data):
    """Test: Crear inspección falla si el usuario no es INSPECTOR"""
    with app.app_context():
        token = get_auth_token(client, app, "duenio_test@example.com", "password123", "DUENIO")
        headers = {'Authorization': f'Bearer {token}'}
        
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 9},
                {"descripcion": "Frenos", "puntuacion": 8},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 7},
                {"descripcion": "Chasis y estructura", "puntuacion": 9},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 8},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 9}
            ]
        }
        
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert 'error' in response_data


def test_create_inspection_without_token(client, app, setup_data):
    """Test: Crear inspección falla sin token JWT"""
    with app.app_context():
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 9},
                {"descripcion": "Frenos", "puntuacion": 8},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 7},
                {"descripcion": "Chasis y estructura", "puntuacion": 9},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 8},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 9}
            ]
        }
        
        response = client.post('/api/inspections', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA validaciones de chequeos
# ========================================

def test_create_inspection_invalid_chequeo_count(client, app, setup_data):
    """Test: Crear inspección falla si no son exactamente 8 chequeos"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Intentar crear inspección con solo 5 chequeos
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 8},
                {"descripcion": "Frenos", "puntuacion": 9},
                {"descripcion": "Dirección y suspensión", "puntuacion": 7},
                {"descripcion": "Neumáticos", "puntuacion": 8},
                {"descripcion": "Chasis y estructura", "puntuacion": 10}
            ]
        }
        
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA creación con resultado RECHEQUEAR
# ========================================

def test_create_inspection_resultado_rechequear_por_total_bajo(client, app, setup_data):
    """Test: Crear inspección con resultado RECHEQUEAR por total < 40 (observación obligatoria)"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Intentar crear SIN observación (debe fallar)
        data_sin_obs = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 3},
                {"descripcion": "Frenos", "puntuacion": 4},
                {"descripcion": "Dirección y suspensión", "puntuacion": 5},
                {"descripcion": "Neumáticos", "puntuacion": 5},
                {"descripcion": "Chasis y estructura", "puntuacion": 5},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 5},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 5},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 2}
            ]
        }
        response_sin_obs = client.post('/api/inspections', json=data_sin_obs, headers=headers)
        assert response_sin_obs.status_code == 400
        
        # Crear CON observación
        data_con_obs = {
            **data_sin_obs,
            "observacion": "Problemas graves detectados en frenos y emisiones que requieren reparación inmediata"
        }
        response = client.post('/api/inspections', json=data_con_obs, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['resultado'] == 'RECHEQUEAR'
        assert response_data['puntuacion_total'] == 34
        assert response_data['observacion'] is not None


def test_create_inspection_resultado_rechequear_por_item_bajo(client, app, setup_data):
    """Test: Crear inspección con resultado RECHEQUEAR por algún item < 5"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección con total alto pero un item < 5
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 4},  # < 5!
                {"descripcion": "Frenos", "puntuacion": 10},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 10},
                {"descripcion": "Chasis y estructura", "puntuacion": 10},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 10},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 10}
            ],
            "observacion": "Luces delanteras insuficientes, requiere reemplazo"
        }
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['resultado'] == 'RECHEQUEAR'
        assert response_data['puntuacion_total'] == 74


def test_create_inspection_caso_borde_80_puntos(client, app, setup_data):
    """Test: Caso borde - exactamente 80 puntos con todos >= 5 → SEGURO (nota máxima)"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # 80 puntos (nota máxima) con todos >= 5 → SEGURO
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 10},
                {"descripcion": "Frenos", "puntuacion": 10},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 10},
                {"descripcion": "Chasis y estructura", "puntuacion": 10},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 10},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 10}
            ]
        }
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['puntuacion_total'] == 80
        # Regla: 40 ≤ puntos ≤ 80 Y todos >= 5 → SEGURO
        assert response_data['resultado'] == 'SEGURO'


def test_create_inspection_caso_borde_40_puntos(client, app, setup_data):
    """Test: Caso borde - exactamente 40 puntos con todos >= 5 → SEGURO"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # 40 puntos (límite inferior) con todos >= 5 → SEGURO
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 5},
                {"descripcion": "Frenos", "puntuacion": 5},
                {"descripcion": "Dirección y suspensión", "puntuacion": 5},
                {"descripcion": "Neumáticos", "puntuacion": 5},
                {"descripcion": "Chasis y estructura", "puntuacion": 5},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 5},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 5},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 5}
            ]
        }
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['puntuacion_total'] == 40
        # Regla: 40 ≤ puntos ≤ 80 Y todos >= 5 → SEGURO
        assert response_data['resultado'] == 'SEGURO'


def test_create_inspection_rango_medio_seguro(client, app, setup_data):
    """Test: 60 puntos con todos >= 5 → SEGURO (rango medio 40-80)"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # 60 puntos (rango medio) con todos >= 5 → SEGURO
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 8},
                {"descripcion": "Frenos", "puntuacion": 7},
                {"descripcion": "Dirección y suspensión", "puntuacion": 8},
                {"descripcion": "Neumáticos", "puntuacion": 7},
                {"descripcion": "Chasis y estructura", "puntuacion": 8},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 7},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 8},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 7}
            ]
        }
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['puntuacion_total'] == 60
        # Regla: 40 ≤ puntos ≤ 80 Y todos >= 5 → SEGURO
        assert response_data['resultado'] == 'SEGURO'


def test_create_inspection_fecha_incorrecta(client, app, setup_data):
    """Test: Crear inspección falla si no es el día programado del turno"""
    with app.app_context():
        from datetime import timedelta
        from src.models import Turno
        
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Modificar la fecha del turno para que sea mañana
        turno = Turno.query.filter_by(id=setup_data["turno_id"]).first()
        turno.fecha = datetime.utcnow() + timedelta(days=1)
        db.session.commit()
        
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": f"Chequeo {i}", "puntuacion": 10}
                for i in range(1, 9)
            ]
        }
        
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert 'día programado' in response_data['error'].lower()


# ========================================
# TESTS PARA /api/inspections/{id} (GET - Obtener inspección)
# ========================================

def test_get_inspection_success(client, app, setup_data):
    """Test: Obtener inspección por ID exitosamente"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección completa
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 9},
                {"descripcion": "Frenos", "puntuacion": 8},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 7},
                {"descripcion": "Chasis y estructura", "puntuacion": 9},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 8},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 9}
            ]
        }
        response_inspeccion = client.post('/api/inspections', json=data, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Obtener inspección
        response = client.get(f'/api/inspections/{inspeccion_id}', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['id'] == inspeccion_id
        assert response_data['vehiculo_matricula'] == setup_data["matricula"]


# ========================================
# TESTS PARA /api/inspections/vehiculo/{matricula} (GET)
# ========================================

def test_list_inspections_by_vehiculo(client, app, setup_data):
    """Test: Listar inspecciones de un vehículo"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección completa
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": "Luces y señalización", "puntuacion": 9},
                {"descripcion": "Frenos", "puntuacion": 8},
                {"descripcion": "Dirección y suspensión", "puntuacion": 10},
                {"descripcion": "Neumáticos", "puntuacion": 7},
                {"descripcion": "Chasis y estructura", "puntuacion": 9},
                {"descripcion": "Contaminación y ruidos", "puntuacion": 8},
                {"descripcion": "Elementos de seguridad obligatorios", "puntuacion": 10},
                {"descripcion": "Cinturones, vidrios y espejos", "puntuacion": 9}
            ]
        }
        client.post('/api/inspections', json=data, headers=headers)
        
        # Listar inspecciones del vehículo
        response = client.get(f'/api/vehicles/{setup_data["matricula"]}/inspections', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'inspecciones' in response_data
        assert response_data['total'] >= 1


# ========================================
# TESTS PARA VERIFICAR JWT Y ROLES
# ========================================

def test_crear_inspeccion_sin_token(client, app, setup_data):
    """Test: Crear inspección falla sin token JWT"""
    with app.app_context():
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"],
            "chequeos": [
                {"descripcion": f"Chequeo {i}", "puntuacion": 8}
                for i in range(1, 9)
            ]
        }
        
        response = client.post('/api/inspections', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data



