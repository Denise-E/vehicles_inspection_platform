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
    """Test: Consultar disponibilidad exitosamente"""
    with app.app_context():
        # Calcular fecha futura (próximo lunes)
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # Lunes = 0
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha_inicio": next_monday.strftime('%Y-%m-%d')
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['matricula'] == setup_data["matricula"]
        assert 'slots' in response_data
        assert 'total_disponibles' in response_data
        assert len(response_data['slots']) > 0


def test_consultar_disponibilidad_vehiculo_no_existe(client, app):
    """Test: Consultar disponibilidad falla con vehículo no existente"""
    with app.app_context():
        data = {
            "matricula": "XYZ999"
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "no encontrado" in response_data['error']


def test_consultar_disponibilidad_formato_fecha_invalido(client, app, setup_data):
    """Test: Consultar disponibilidad falla con formato de fecha inválido"""
    with app.app_context():
        data = {
            "matricula": setup_data["matricula"],
            "fecha_inicio": "25/10/2025"  # Formato incorrecto
        }
        
        response = client.post('/api/bookings/disponibilidad', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/bookings/reservar
# ========================================

def test_reservar_turno_success(client, app, setup_data):
    """Test: Reservar turno exitosamente"""
    with app.app_context():
        # Calcular fecha futura (próximo lunes a las 10:00)
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M'),
            "creado_por": setup_data["usuario_id"]
        }
        
        response = client.post('/api/bookings/reservar', json=data)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['matricula'] == setup_data["matricula"]
        assert response_data['estado'] == 'RESERVADO'
        assert 'id' in response_data


def test_reservar_turno_fecha_pasada(client, app, setup_data):
    """Test: Reservar turno falla con fecha pasada"""
    with app.app_context():
        # Fecha del pasado
        fecha_pasada = datetime.now() - timedelta(days=7)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_pasada.strftime('%Y-%m-%d %H:%M'),
            "creado_por": setup_data["usuario_id"]
        }
        
        response = client.post('/api/bookings/reservar', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "futura" in response_data['error']


def test_reservar_turno_dia_no_laborable(client, app, setup_data):
    """Test: Reservar turno falla en sábado"""
    with app.app_context():
        # Calcular próximo sábado
        today = datetime.now()
        days_ahead = 5 - today.weekday()  # Sábado = 5
        if days_ahead <= 0:
            days_ahead += 7
        next_saturday = today + timedelta(days=days_ahead)
        fecha_turno = next_saturday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M'),
            "creado_por": setup_data["usuario_id"]
        }
        
        response = client.post('/api/bookings/reservar', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "lunes a viernes" in response_data['error']


def test_reservar_turno_horario_invalido(client, app, setup_data):
    """Test: Reservar turno falla fuera del horario 9-20hs"""
    with app.app_context():
        # Próximo lunes a las 8:00 (antes del horario)
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=8, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": setup_data["matricula"],
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M'),
            "creado_por": setup_data["usuario_id"]
        }
        
        response = client.post('/api/bookings/reservar', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_reservar_turno_duplicado(client, app, setup_data):
    """Test: Reservar turno falla si ya existe uno en la misma fecha"""
    with app.app_context():
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
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M'),
            "creado_por": setup_data["usuario_id"]
        }
        
        response = client.post('/api/bookings/reservar', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "Ya existe" in response_data['error']


def test_reservar_turno_vehiculo_no_existe(client, app, setup_data):
    """Test: Reservar turno falla si el vehículo no existe"""
    with app.app_context():
        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        fecha_turno = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        data = {
            "matricula": "ZZZ999",
            "fecha": fecha_turno.strftime('%Y-%m-%d %H:%M'),
            "creado_por": setup_data["usuario_id"]
        }
        
        response = client.post('/api/bookings/reservar', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/bookings/{id}/confirmar
# ========================================

def test_confirmar_turno_success(client, app, setup_data):
    """Test: Confirmar turno exitosamente"""
    with app.app_context():
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
        response = client.put(f'/api/bookings/{turno_id}/confirmar')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['estado'] == 'CONFIRMADO'
        assert response_data['id'] == turno_id


def test_confirmar_turno_no_encontrado(client, app):
    """Test: Confirmar turno falla si el turno no existe"""
    with app.app_context():
        response = client.put('/api/bookings/999/confirmar')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_confirmar_turno_estado_invalido(client, app, setup_data):
    """Test: Confirmar turno falla si ya está en otro estado"""
    with app.app_context():
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
        response = client.put(f'/api/bookings/{turno_id}/confirmar')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/bookings/{id}/cancelar
# ========================================

def test_cancelar_turno_success(client, app, setup_data):
    """Test: Cancelar turno exitosamente"""
    with app.app_context():
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
        response = client.put(f'/api/bookings/{turno_id}/cancelar')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['estado'] == 'CANCELADO'
        assert response_data['id'] == turno_id


# ========================================
# TESTS PARA /api/bookings/{id}
# ========================================

def test_obtener_turno_success(client, app, setup_data):
    """Test: Obtener turno por ID exitosamente"""
    with app.app_context():
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
        response = client.get(f'/api/bookings/{turno_id}')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['id'] == turno_id
        assert response_data['matricula'] == setup_data["matricula"]


def test_obtener_turno_no_encontrado(client, app):
    """Test: Obtener turno falla si no existe"""
    with app.app_context():
        response = client.get('/api/bookings/999')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/bookings/usuario/{user_id}
# ========================================

def test_listar_turnos_por_usuario_success(client, app, setup_data):
    """Test: Listar turnos de un usuario exitosamente"""
    with app.app_context():
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
        response = client.get(f'/api/bookings/usuario/{setup_data["usuario_id"]}')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'turnos' in response_data
        assert response_data['total'] >= 2


# ========================================
# TESTS PARA /api/bookings/vehiculo/{matricula}
# ========================================

def test_listar_turnos_por_vehiculo_success(client, app, setup_data):
    """Test: Listar turnos de un vehículo exitosamente"""
    with app.app_context():
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
        response = client.get(f'/api/bookings/vehiculo/{setup_data["matricula"]}')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'turnos' in response_data
        assert response_data['total'] >= 1

