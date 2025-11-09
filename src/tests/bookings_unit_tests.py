import pytest
import os
from datetime import datetime, timedelta
from src import create_app, db
from src.models import Usuario, UsuarioRol, Vehiculo, EstadoVehiculo, Turno, EstadoTurno
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
        
        # Crear roles necesarios
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


def get_auth_token(client, app, mail="test_booking@example.com", password="password123", role="DUENIO"):
    """
    Helper function para obtener un token JWT creando y haciendo login con un usuario.
    
    Returns:
        str: Token JWT
    """
    with app.app_context():
        # Crear usuario si no existe
        rol = UsuarioRol.query.filter_by(nombre=role).first()
        existing_user = Usuario.query.filter_by(mail=mail).first()
        
        if not existing_user:
            user = Usuario(
                nombre_completo="Test Booking User",
                mail=mail,
                telefono="123456789",
                hash_password=hash_password(password),
                rol_id=rol.id,
                activo=True
            )
            db.session.add(user)
            db.session.commit()
        
        # Hacer login
        login_data = {
            "mail": mail,
            "contrasenia": password
        }
        response = client.post('/api/users/login', json=login_data)
        return response.get_json()['token']


@pytest.fixture
def setup_data(app):
    """Crea datos de prueba (usuarios y vehículos)"""
    with app.app_context():
        # Crear usuario dueño
        rol_duenio = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        usuario = Usuario(
            nombre_completo="Juan Perez",
            mail="juan@example.com",
            telefono="123456789",
            hash_password=hash_password("password123"),
            rol_id=rol_duenio.id,
            activo=True
        )
        db.session.add(usuario)
        db.session.commit()
        
        # Crear vehículo
        estado_activo = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehiculo = Vehiculo(
            matricula="ABC123",
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            duenio_id=usuario.id,
            estado_id=estado_activo.id
        )
        db.session.add(vehiculo)
        db.session.commit()
        
        return {
            "usuario_id": usuario.id,
            "vehiculo_id": vehiculo.id,
            "matricula": vehiculo.matricula
        }


# ========================================
# TESTS PARA /api/bookings/disponibilidad
# ========================================

def test_consultar_disponibilidad_success(client, app, setup_data):
    """Test: Consultar disponibilidad general del sistema exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Calcular fecha futura (próximo lunes)
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # Lunes = 0
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        
        data = {
            "fecha_inicio": next_monday.strftime('%Y-%m-%d')
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'slots' in response_data
        assert 'total_disponibles' in response_data
        assert len(response_data['slots']) > 0


def test_consultar_disponibilidad_con_rango_fechas(client, app):
    """Test: Consultar disponibilidad con rango de fechas con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Calcular rango de fechas (próximos 7 días)
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        fecha_inicio = today + timedelta(days=days_ahead)
        fecha_final = fecha_inicio + timedelta(days=6)
        
        data = {
            "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
            "fecha_final": fecha_final.strftime('%Y-%m-%d')
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'slots' in response_data
        assert 'total_disponibles' in response_data
        assert len(response_data['slots']) > 0


def test_consultar_disponibilidad_formato_fecha_invalido(client, app, setup_data):
    """Test: Consultar disponibilidad falla con formato de fecha inválido con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        data = {
            "fecha_inicio": "25/10/2025"  # Formato incorrecto
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_consultar_disponibilidad_rango_invalido(client, app):
    """Test: Consultar disponibilidad falla si fecha_final es anterior a fecha_inicio con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        data = {
            "fecha_inicio": "2025-11-01",
            "fecha_final": "2025-10-25"  # Anterior a fecha_inicio
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_consultar_disponibilidad_sin_body(client, app):
    """Test: Consultar disponibilidad sin body (usa valores por defecto) con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Sin body - debe usar valores por defecto
        response = client.post('/api/bookings/disponibilidad', json={}, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'slots' in response_data
        assert 'total_disponibles' in response_data


# ========================================
# TESTS PARA /api/bookings
# ========================================

def test_reservar_turno_success(client, app, setup_data):
    """Test: Reservar turno exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Calcular fecha futura (próximo lunes a las 10:00)
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['matricula'] == setup_data["matricula"]
        assert response_data['estado'] == 'RESERVADO'
        assert 'id' in response_data
        assert 'creado_por' in response_data


def test_reservar_turno_fecha_pasada(client, app, setup_data):
    """Test: Reservar turno falla con fecha pasada con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Fecha del pasado
        fecha_pasada = datetime.now() - timedelta(days=7)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_pasada.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "futura" in response_data['error']


def test_reservar_turno_dia_no_laborable(client, app, setup_data):
    """Test: Reservar turno falla en sábado con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Calcular próximo sábado
        today = datetime.now()
        days_ahead = 5 - today.weekday()  # Sábado = 5
        if days_ahead <= 0:
            days_ahead += 7
        next_saturday = today + timedelta(days=days_ahead)
        fecha_turno = next_saturday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "lunes a viernes" in response_data['error']


def test_reservar_turno_horario_invalido(client, app, setup_data):
    """Test: Reservar turno falla fuera del horario 9-20hs con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Próximo lunes a las 8:00 (antes del horario)
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=8, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_reservar_turno_duplicado(client, app, setup_data):
    """Test: Reservar turno falla si ya existe uno en la misma fecha con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear un turno previo
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        estado_reservado = EstadoTurno.query.filter_by(nombre='RESERVADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno_existente = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_reservado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add(turno_existente)
        db.session.commit()
        
        # Intentar crear otro turno en la misma fecha
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "Ya existe" in response_data['error']


def test_reservar_turno_vehiculo_no_existe(client, app, setup_data):
    """Test: Reservar turno falla si el vehículo no existe con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": "ZZZ999",
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_reservar_turno_vehiculo_no_propio(client, app):
    """Test: Usuario normal no puede crear turno para vehículo de otro usuario con JWT"""
    with app.app_context():
        # Crear un segundo usuario (dueño de otro vehículo)
        rol_duenio = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        otro_usuario = Usuario(
            nombre_completo="Maria Lopez",
            mail="maria@example.com",
            telefono="987654321",
            hash_password=hash_password("password123"),
            rol_id=rol_duenio.id,
            activo=True
        )
        db.session.add(otro_usuario)
        db.session.commit()
        
        # Crear vehículo del segundo usuario
        estado_activo = EstadoVehiculo.query.filter_by(nombre='ACTIVO').first()
        vehiculo_otro = Vehiculo(
            matricula="XYZ789",
            marca="Ford",
            modelo="Focus",
            anio=2021,
            duenio_id=otro_usuario.id,
            estado_id=estado_activo.id
        )
        db.session.add(vehiculo_otro)
        db.session.commit()
        
        # Obtener token del primer usuario (que NO es dueño del vehículo XYZ789)
        token = get_auth_token(client, app, mail="test_booking@example.com")
        headers = {'Authorization': f'Bearer {token}'}
        
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": "XYZ789",  # Vehículo de OTRO usuario
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "No tienes permiso" in response_data['error'] or "propios vehículos" in response_data['error']


def test_reservar_turno_vehiculo_inactivo(client, app, setup_data):
    """Test: Usuario normal no puede crear turno para vehículo inactivo con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Cambiar el estado del vehículo a INACTIVO
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        estado_inactivo = EstadoVehiculo.query.filter_by(nombre='INACTIVO').first()
        vehiculo.estado_id = estado_inactivo.id
        db.session.commit()
        
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "ACTIVO" in response_data['error'] or "estado" in response_data['error']


def test_reservar_turno_admin_cualquier_vehiculo(client, app, setup_data):
    """Test: Usuario ADMIN puede crear turno para cualquier vehículo con JWT"""
    with app.app_context():
        # Obtener token de un usuario ADMIN
        token = get_auth_token(client, app, mail="admin@example.com", role="ADMIN")
        headers = {'Authorization': f'Bearer {token}'}
        
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],  # Vehículo de otro usuario
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        
        response = client.post('/api/bookings', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['matricula'] == setup_data["matricula"]
        assert response_data['estado'] == 'RESERVADO'
        assert 'id' in response_data


# ========================================
# TESTS PARA /api/bookings/{id}/confirmar
# ========================================

def test_confirmar_turno_success(client, app, setup_data):
    """Test: Confirmar turno exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear un turno en estado RESERVADO
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=11, minute=0, second=0, microsecond=0)
        
        estado_reservado = EstadoTurno.query.filter_by(nombre='RESERVADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_reservado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add(turno)
        db.session.commit()
        turno_id = turno.id
        
        # Confirmar el turno
        response = client.put(f'/api/bookings/{turno_id}/confirmar', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['estado'] == 'CONFIRMADO'
        assert response_data['id'] == turno_id


def test_confirmar_turno_no_encontrado(client, app):
    """Test: Confirmar turno falla si el turno no existe con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.put('/api/bookings/999/confirmar', headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_confirmar_turno_estado_invalido(client, app, setup_data):
    """Test: Confirmar turno falla si ya está en otro estado con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear un turno en estado CANCELADO
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=12, minute=0, second=0, microsecond=0)
        
        estado_cancelado = EstadoTurno.query.filter_by(nombre='CANCELADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_cancelado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add(turno)
        db.session.commit()
        turno_id = turno.id
        
        # Intentar confirmar
        response = client.put(f'/api/bookings/{turno_id}/confirmar', headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/bookings/{id}/cancelar
# ========================================

def test_cancelar_turno_success(client, app, setup_data):
    """Test: Cancelar turno exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear un turno en estado RESERVADO
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=13, minute=0, second=0, microsecond=0)
        
        estado_reservado = EstadoTurno.query.filter_by(nombre='RESERVADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_reservado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add(turno)
        db.session.commit()
        turno_id = turno.id
        
        # Cancelar el turno
        response = client.put(f'/api/bookings/{turno_id}/cancelar', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['estado'] == 'CANCELADO'
        assert response_data['id'] == turno_id


# ========================================
# TESTS PARA /api/bookings/{id}
# ========================================

def test_obtener_turno_success(client, app, setup_data):
    """Test: Obtener turno por ID exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear un turno
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=14, minute=0, second=0, microsecond=0)
        
        estado_reservado = EstadoTurno.query.filter_by(nombre='RESERVADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno = Turno(
            vehiculo_id=vehiculo.id,
            fecha=fecha_turno,
            estado_id=estado_reservado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add(turno)
        db.session.commit()
        turno_id = turno.id
        
        # Obtener el turno
        response = client.get(f'/api/bookings/{turno_id}', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['id'] == turno_id
        assert response_data['matricula'] == setup_data["matricula"]


def test_obtener_turno_no_encontrado(client, app):
    """Test: Obtener turno falla si no existe con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/bookings/999', headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/bookings/usuario/{user_id}
# ========================================

def test_listar_turnos_por_usuario_success(client, app, setup_data):
    """Test: Listar turnos de un usuario exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear turnos
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        
        estado_reservado = EstadoTurno.query.filter_by(nombre='RESERVADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno1 = Turno(
            vehiculo_id=vehiculo.id,
            fecha=next_monday.replace(hour=15, minute=0, second=0, microsecond=0),
            estado_id=estado_reservado.id,
            creado_por=setup_data["usuario_id"]
        )
        turno2 = Turno(
            vehiculo_id=vehiculo.id,
            fecha=next_monday.replace(hour=16, minute=0, second=0, microsecond=0),
            estado_id=estado_reservado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add_all([turno1, turno2])
        db.session.commit()
        
        # Listar turnos
        response = client.get(f'/api/bookings/usuario/{setup_data["usuario_id"]}', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'turnos' in response_data
        assert response_data['total'] >= 2


# ========================================
# TESTS PARA /api/bookings/vehiculo/{matricula}
# ========================================

def test_listar_turnos_por_vehiculo_success(client, app, setup_data):
    """Test: Listar turnos de un vehículo exitosamente con JWT"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Crear turnos
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        
        estado_confirmado = EstadoTurno.query.filter_by(nombre='CONFIRMADO').first()
        vehiculo = Vehiculo.query.filter_by(matricula=setup_data["matricula"]).first()
        
        turno1 = Turno(
            vehiculo_id=vehiculo.id,
            fecha=next_monday.replace(hour=17, minute=0, second=0, microsecond=0),
            estado_id=estado_confirmado.id,
            creado_por=setup_data["usuario_id"]
        )
        db.session.add(turno1)
        db.session.commit()
        
        # Listar turnos
        response = client.get(f'/api/bookings/vehiculo/{setup_data["matricula"]}', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'turnos' in response_data
        assert response_data['total'] >= 1


# ========================================
# TESTS PARA VERIFICAR AUTENTICACIÓN JWT (401 sin token)
# ========================================

def test_disponibilidad_without_token(client, app, setup_data):
    """Test: Consultar disponibilidad falla sin token JWT"""
    with app.app_context():
        data = {}
        response = client.post('/api/bookings/disponibilidad', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_reservar_without_token(client, app, setup_data):
    """Test: Reservar turno falla sin token JWT"""
    with app.app_context():
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M')
        }
        response = client.post('/api/bookings', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_confirmar_without_token(client, app):
    """Test: Confirmar turno falla sin token JWT"""
    with app.app_context():
        response = client.put('/api/bookings/1/confirmar')
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_cancelar_without_token(client, app):
    """Test: Cancelar turno falla sin token JWT"""
    with app.app_context():
        response = client.put('/api/bookings/1/cancelar')
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_obtener_turno_without_token(client, app):
    """Test: Obtener turno falla sin token JWT"""
    with app.app_context():
        response = client.get('/api/bookings/1')
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_listar_por_usuario_without_token(client, app):
    """Test: Listar turnos por usuario falla sin token JWT"""
    with app.app_context():
        response = client.get('/api/bookings/usuario/1')
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_listar_por_vehiculo_without_token(client, app):
    """Test: Listar turnos por vehículo falla sin token JWT"""
    with app.app_context():
        response = client.get('/api/bookings/vehiculo/ABC123')
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data

