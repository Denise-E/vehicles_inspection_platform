import pytest
import os
from datetime import datetime, timedelta
from src import create_app, db
from src.models import (
    Usuario, UsuarioRol, Vehiculo, EstadoVehiculo, 
    Turno, EstadoTurno, Inspeccion, ResultadoInspeccion, Chequeo
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
            rechequear = EstadoVehiculo(nombre='RECHEQUEAR')
            db.session.add_all([activo, inactivo, rechequear])
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
        
        # Crear turno CONFIRMADO
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
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

def test_create_inspection_success(client, app, setup_data):
    """Test: Crear inspección exitosamente con rol INSPECTOR"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        
        response = client.post('/api/inspections', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['turno_id'] == setup_data["turno_id"]
        assert response_data['vehiculo_matricula'] == setup_data["matricula"]
        assert response_data['estado'] == 'PENDIENTE'
        assert 'id' in response_data


def test_create_inspection_without_inspector_role(client, app, setup_data):
    """Test: Crear inspección falla si el usuario no es INSPECTOR"""
    with app.app_context():
        token = get_auth_token(client, app, "duenio_test@example.com", "password123", "DUENIO")
        headers = {'Authorization': f'Bearer {token}'}
        
        data = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
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
            "inspector_id": setup_data["inspector_id"]
        }
        
        response = client.post('/api/inspections', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/inspections/{id}/chequeos (POST - Registrar chequeos)
# ========================================

def test_register_chequeos_success(client, app, setup_data):
    """Test: Registrar 8 chequeos exitosamente"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección primero
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Registrar 8 chequeos
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 8},
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 9},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 7},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 8},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 10},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 9},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 8},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 9}
            ]
        }
        
        response = client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['estado'] == 'EN_PROCESO'


def test_register_chequeos_invalid_count(client, app, setup_data):
    """Test: Registrar chequeos falla si no son exactamente 8"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Intentar registrar solo 5 chequeos
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 8},
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 9},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 7},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 8},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 10}
            ]
        }
        
        response = client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/inspections/{id}/cerrar (POST - Cerrar inspección)
# ========================================

def test_close_inspection_resultado_seguro(client, app, setup_data):
    """Test: Cerrar inspección con resultado SEGURO (suma > 80 y todos >= 5)"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Registrar chequeos con total > 80 y todos >= 5
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 10},
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 10},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 10},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 10},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 10},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 10},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 10},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 10}
            ]
        }
        client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        # Cerrar inspección (sin observación, ya que es SEGURO)
        response = client.patch(f'/api/inspections/{inspeccion_id}', json={}, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['resultado'] == 'SEGURO'
        assert response_data['puntuacion_total'] == 80


def test_close_inspection_resultado_rechequear_por_total_bajo(client, app, setup_data):
    """Test: Cerrar inspección con resultado RECHEQUEAR por total < 40"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Registrar chequeos con total < 40
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 3},
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 4},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 5},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 5},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 5},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 5},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 5},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 2}
            ]
        }
        client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        # Intentar cerrar SIN observación (debe fallar)
        response_sin_obs = client.patch(f'/api/inspections/{inspeccion_id}', json={}, headers=headers)
        assert response_sin_obs.status_code == 400
        
        # Cerrar CON observación
        data_close = {"observacion": "Problemas graves detectados en frenos y emisiones que requieren reparación inmediata"}
        response = client.patch(f'/api/inspections/{inspeccion_id}', json=data_close, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['resultado'] == 'RECHEQUEAR'
        assert response_data['puntuacion_total'] == 34
        assert response_data['observacion'] is not None


def test_close_inspection_resultado_rechequear_por_item_bajo(client, app, setup_data):
    """Test: Cerrar inspección con resultado RECHEQUEAR por algún item < 5"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Registrar chequeos: total alto pero un item < 5
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 4},  # < 5!
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 10},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 10},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 10},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 10},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 10},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 10},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 10}
            ]
        }
        client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        # Cerrar CON observación
        data_close = {"observacion": "Frenos delanteros insuficientes, requiere reemplazo"}
        response = client.patch(f'/api/inspections/{inspeccion_id}', json=data_close, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['resultado'] == 'RECHEQUEAR'
        assert response_data['puntuacion_total'] == 74


def test_close_inspection_caso_borde_80_puntos(client, app, setup_data):
    """Test: Caso borde - exactamente 80 puntos con todos los items >= 5 → SEGURO"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Total = 80 (puntuación perfecta) con todos los items >= 5
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 10},
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 10},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 10},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 10},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 10},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 10},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 10},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 10}
            ]
        }
        
        client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        # Cerrar sin observación (ya que debería ser SEGURO)
        response = client.patch(f'/api/inspections/{inspeccion_id}', json={}, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['puntuacion_total'] == 80
        # Regla: >= 80 Y todos >= 5 → SEGURO
        assert response_data['resultado'] == 'SEGURO'


def test_close_inspection_80_puntos_con_item_bajo(client, app, setup_data):
    """Test: 80 puntos pero con un item < 5 → RECHEQUEAR (falla condición de todos >= 5)"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Nota: Es matemáticamente imposible llegar a exactamente 80 puntos con un item < 5
        # porque 7 items * 10 puntos = 70, más 1 item < 5 = máximo 74 puntos
        # Pero podemos usar valores intermedios para ilustrar el caso
        # Ejemplo: total alto pero un item < 5
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 4},  # < 5!
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 10},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 10},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 10},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 10},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 10},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 10},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 10}
            ]
        }
        # Total = 74 (no 80), pero ilustra que incluso con total alto, un item < 5 → RECHEQUEAR
        
        client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        # Cerrar CON observación
        data_close = {"observacion": "Los frenos no cumplen con el estándar mínimo requerido"}
        response = client.patch(f'/api/inspections/{inspeccion_id}', json=data_close, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['puntuacion_total'] == 74
        assert response_data['resultado'] == 'RECHEQUEAR'


def test_close_inspection_caso_borde_40_puntos(client, app, setup_data):
    """Test: Caso borde - exactamente 40 puntos → RECHEQUEAR"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
        inspeccion_id = response_inspeccion.get_json()['id']
        
        # Total = 40
        data_chequeos = {
            "chequeos": [
                {"item_numero": 1, "descripcion": "Frenos", "puntuacion": 5},
                {"item_numero": 2, "descripcion": "Luces", "puntuacion": 5},
                {"item_numero": 3, "descripcion": "Neumáticos", "puntuacion": 5},
                {"item_numero": 4, "descripcion": "Dirección", "puntuacion": 5},
                {"item_numero": 5, "descripcion": "Suspensión", "puntuacion": 5},
                {"item_numero": 6, "descripcion": "Motor", "puntuacion": 5},
                {"item_numero": 7, "descripcion": "Chasis", "puntuacion": 5},
                {"item_numero": 8, "descripcion": "Emisiones", "puntuacion": 5}
            ]
        }
        client.post(f'/api/inspections/{inspeccion_id}/chequeos', json=data_chequeos, headers=headers)
        
        # Cerrar CON observación
        data_close = {"observacion": "Puntuación mínima aceptable, requiere monitoreo"}
        response = client.patch(f'/api/inspections/{inspeccion_id}', json=data_close, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['puntuacion_total'] == 40
        # Regla: <40 → RECHEQUEAR, pero =40 cae en el else (no <40 pero tampoco >80)
        assert response_data['resultado'] == 'RECHEQUEAR'


# ========================================
# TESTS PARA /api/inspections/{id} (GET - Obtener inspección)
# ========================================

def test_get_inspection_success(client, app, setup_data):
    """Test: Obtener inspección por ID exitosamente"""
    with app.app_context():
        token = get_auth_token(client, app, "inspector_test@example.com", "password123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        response_inspeccion = client.post('/api/inspections', json=data_inspeccion, headers=headers)
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
        
        # Crear inspección
        data_inspeccion = {
            "turno_id": setup_data["turno_id"],
            "inspector_id": setup_data["inspector_id"]
        }
        client.post('/api/inspections', json=data_inspeccion, headers=headers)
        
        # Listar inspecciones del vehículo
        response = client.get(f'/api/vehicles/{setup_data["matricula"]}/inspections', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'inspecciones' in response_data
        assert response_data['total'] >= 1


# ========================================
# TESTS PARA VERIFICAR JWT Y ROLES
# ========================================

def test_register_chequeos_without_token(client, app, setup_data):
    """Test: Registrar chequeos falla sin token JWT"""
    with app.app_context():
        data_chequeos = {
            "chequeos": [
                {"item_numero": i, "descripcion": f"Chequeo {i}", "puntuacion": 8}
                for i in range(1, 9)
            ]
        }
        
        response = client.post('/api/inspections/1/chequeos', json=data_chequeos)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_close_inspection_without_inspector_role(client, app, setup_data):
    """Test: Cerrar inspección falla si el usuario no es INSPECTOR"""
    with app.app_context():
        token = get_auth_token(client, app, "duenio_test@example.com", "password123", "DUENIO")
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.patch('/api/inspections/1', json={}, headers=headers)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert 'error' in response_data

