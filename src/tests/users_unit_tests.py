import pytest
import os
from src import create_app, db
from src.models import Usuario, UsuarioRol
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
            cliente_rol = UsuarioRol(nombre='DUENIO')
            
            db.session.add_all([admin_rol, inspector_rol, cliente_rol])
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


def get_auth_token(client, app, mail="test@example.com", password="password123", role="DUENIO"):
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
                nombre_completo="Test User",
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
        response = client.post('/api/users/sessions', json=login_data)
        return response.get_json()['token']


# ========================================
# TESTS PARA /api/users
# ========================================

def test_register_user_success(client, app):
    """Test: Registro exitoso de un usuario"""
    with app.app_context():
        data = {
            "nombre_completo": "Juan Perez",
            "mail": "juan@example.com",
            "telefono": "123456789",
            "contrasenia": "password123",
            "rol": "DUENIO"
        }
        
        response = client.post('/api/users', json=data)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['nombre_completo'] == "Juan Perez"
        assert response_data['mail'] == "juan@example.com"
        assert response_data['rol'] == "DUENIO"
        assert response_data['activo']
        assert 'id' in response_data


def test_register_user_short_password(client, app):
    """Test: Registro falla con contraseña menor a 6 caracteres"""
    with app.app_context():
        data = {
            "nombre_completo": "Maria Lopez",
            "mail": "maria@example.com",
            "telefono": "987654321",
            "contrasenia": "12345",  # Contraseña con menos de 6 caracteres
            "rol": "DUENIO"
        }
        
        response = client.post('/api/users', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


def test_register_user_duplicate_email(client, app):
    """Test: Registro falla con email ya registrado"""
    with app.app_context():
        # Crear usuario previo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        existing_user = Usuario(
            nombre_completo="Denise Existente",
            mail="denise@example.com",
            telefono="111222333",
            hash_password=hash_password("password123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(existing_user)
        db.session.commit()
        
        # Intentar registrar con el mismo email
        data = {
            "nombre_completo": "Denise Nueva",
            "mail": "denise@example.com",
            "telefono": "444555666",
            "contrasenia": "password456",
            "rol": "DUENIO"
        }
        
        response = client.post('/api/users', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data


# ========================================
# TESTS PARA /api/users/sessions (login)
# ========================================

def test_login_user_success(client, app):
    """Test: Login exitoso de un usuario y retorna token JWT"""
    with app.app_context():
        # Crear usuario previo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Carlos Rodriguez",
            mail="carlos@example.com",
            telefono="555666777",
            hash_password=hash_password("mypassword123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Intentar login
        data = {
            "mail": "carlos@example.com",
            "contrasenia": "mypassword123"
        }
        
        response = client.post('/api/users/sessions', json=data)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['nombre_completo'] == "Carlos Rodriguez"
        assert response_data['mail'] == "carlos@example.com"
        assert response_data['activo']
        assert 'token' in response_data
        assert len(response_data['token']) > 0


def test_login_user_invalid_password(client, app):
    """Test: Login falla con contraseña inválida"""
    with app.app_context():
        # Crear usuario previo
        rol = UsuarioRol.query.filter_by(nombre='DUENIO').first()
        user = Usuario(
            nombre_completo="Ana Martinez",
            mail="ana@example.com",
            telefono="888999000",
            hash_password=hash_password("correctpassword"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Intentar login con contraseña incorrecta
        data = {
            "mail": "ana@example.com",
            "contrasenia": "wrongpassword"
        }
        
        response = client.post('/api/users/sessions', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "Contraseña incorrecta" in response_data['error']


def test_login_user_email_not_found(client, app):
    """Test: Login falla con email no registrado"""
    with app.app_context():
        data = {
            "mail": "noexiste@example.com",
            "contrasenia": "password123"
        }
        
        response = client.post('/api/users/sessions', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "Usuario no encontrado" in response_data['error']


# ========================================
# TESTS PARA /api/users/{user_id} 
# ========================================

def test_get_user_profile_success(client, app):
    """Test: Obtener perfil de usuario exitosamente con JWT"""
    with app.app_context():
        # Crear usuario previo
        rol = UsuarioRol.query.filter_by(nombre='INSPECTOR').first()
        user = Usuario(
            nombre_completo="Luis Gonzalez",
            mail="luis@example.com",
            telefono="222333444",
            hash_password=hash_password("inspector123"),
            rol_id=rol.id,
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Obtener token
        token = get_auth_token(client, app, "luis@example.com", "inspector123", "INSPECTOR")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Obtener perfil
        response = client.get(f'/api/users/{user_id}', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['nombre_completo'] == "Luis Gonzalez"
        assert response_data['mail'] == "luis@example.com"
        assert response_data['rol'] == "INSPECTOR"
        assert response_data['id'] == user_id


def test_get_user_profile_without_token(client, app):
    """Test: Obtener perfil falla sin token JWT"""
    with app.app_context():
        # Intentar obtener perfil sin token
        response = client.get('/api/users/1')
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert 'error' in response_data


def test_get_user_profile_not_found(client, app):
    """Test: Obtener perfil falla con usuario no encontrado"""
    with app.app_context():
        # Obtener token
        token = get_auth_token(client, app)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Intentar obtener perfil con ID 999 (no existente)
        response = client.get('/api/users/999', headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert "Usuario no encontrado" in response_data['error']

