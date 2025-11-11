# vehicles_inspection_platform
University integrative project – vehicle inspection booking &amp; safety evaluation system built with Python and Flask.

## Descripción del Proyecto

Sistema de gestión de inspecciones vehiculares que permite:
- Registro de vehículos y usuarios
- Reserva y confirmación de turnos de inspección
- Realización de inspecciones técnicas con 8 chequeos obligatorios
- Cálculo automático de resultados (SEGURO/RECHEQUEAR)
- Gestión de roles (DUENIO, INSPECTOR, ADMIN)
- Autenticación mediante JWT

## Requisitos

- Python 3.11
- pip (Administrador de paquetes de Python)
- MySQL 8.0 o superior

## Configuración del Entorno de Desarrollo
Para este proyecto, utilizar la consola Command Prompt para correr los siguientes comandos.

### Paso 1: Crear y Activar el Entorno Virtual

En todos los sistemas operativos:

``` command prompt
python -m venv venv

o

py -m venv venv

El segundo "venv" es el nombre que uno decide ponerle al entorno virtual, se acostumbra a usar venv o env.
```

Para activar el entorno virtual en Windows:

``` command propmt
venv\Scripts\activate
```

Para activar el entorno virtual en macOS/Linux:

```bash
source venv/bin/activate
```
Una vez activado se debe ver (venv) o el nombre que le hayan puesto al enotorno a la izquierda de la ubicación de la carpeta
### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar la Base de Datos

1. Crear la base de datos MySQL ejecutando el script SQL o manualmente desde tu sistema de gestión de bases de datos de preferencia:

```bash
mysql -u root -p < vehicles_db_creation.sql
```

2. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=vehicles_db
SECRET_KEY=tu_clave_secreta  # Usada para la generación de tokens JWT
```

## Estructura del Proyecto

```
vehicles_inspection_platform/
├── src/
│   ├── controllers/       # Lógica de controladores
│   ├── models/            # Modelos de base de datos (SQLAlchemy)
│   ├── routes/            # Definición de rutas/endpoints
│   ├── schemas/           # Validación de datos de entrada y salida (Pydantic)
│   ├── services/          # Lógica de negocio
│   ├── tests/             # Tests unitarios
│   └── utils/             # Utilidades (JWT)
├── templates/             # Plantillas HTML (Swagger UI)
├── app.py                 # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias del proyecto
└── vehicles_db_creation.sql  # Script de creación de BD
```

## Ejecutar el Proyecto

### Paso 1: Navegar al Directorio del Proyecto

```bash
cd ruta/vehicles_inspection_platform
```

### Paso 2: Levantar el proyecto de Flask

```command prompt
flask run
```
Para que el servidor recargue automáticamente cuando se realicen cambios en el código, se lo puede correr con el siguiente comando: 

```command prompt
flask run --reload
```

## Ejecutar Tests

El proyecto incluye tests unitarios para asegurar la calidad del código. Los tests están ubicados en la carpeta `src/tests/`.

### Ejecutar todos los tests

```bash
pytest src/tests/ -v
```

### Ejecutar tests de un módulo específico

Ejemplo para ejecutar solo los tests de usuarios:

```bash
pytest src/tests/users_unit_tests.py -v
```

Para el resto de los tests simplemente se debe mencionar al archivo correspondiente que se desea correr.

### Ejecutar un test específico

```bash
pytest src/tests/users_unit_tests.py::test_register_user_success -v
```

### Documentación de la API

La documentación del proyecto está disponible en la ruta /docs. Puedes acceder a ella navegando a http://localhost:5000/docs una vez que el servidor esté en funcionamiento.

Si se quiere visualizar la documentación en formato JSON esta puede ser accedida desde http://localhost:5000/swagger

## Endpoints Principales

### Usuarios (`/api/users`)
- `POST /api/users/register` - Registrar nuevo usuario
- `POST /api/users/login` - Iniciar sesión (obtener JWT token)
- `GET /api/users` - Listar todos los usuarios (solo ADMIN)

### Vehículos (`/api/vehicles`)
- `POST /api/vehicles` - Registrar nuevo vehículo
- `GET /api/vehicles` - Listar vehículos según rol
- `GET /api/vehicles/<matricula>` - Obtener detalles de un vehículo
- `PUT /api/vehicles/<matricula>` - Actualizar vehículo
- `DELETE /api/vehicles/<matricula>` - Eliminar vehículo (solo ADMIN)

### Turnos (`/api/bookings`)
- `POST /api/bookings` - Crear turno para inspección
- `GET /api/bookings` - Listar turnos según rol
- `PUT /api/bookings/<turno_id>/confirm` - Confirmar turno (ADMIN/INSPECTOR)
- `PUT /api/bookings/<turno_id>/cancel` - Cancelar turno

### Inspecciones (`/api/inspections`)
- `POST /api/inspections` - Crear inspección completa (ADMIN/INSPECTOR)
- `GET /api/inspections/<inspeccion_id>` - Ver detalles de inspección
- `GET /api/inspections` - Listar todas las inspecciones (solo ADMIN)

## Roles de Usuario

### DUENIO
- Registrar y gestionar sus propios vehículos
- Crear turnos de inspección para sus vehículos
- Ver inspecciones de sus vehículos
- Cancelar turnos en estado RESERVADO

### INSPECTOR
- Confirmar turnos
- Realizar inspecciones (crear con 8 chequeos)
- Ver inspecciones realizadas
- Acceso a turnos confirmados

### ADMIN
- Acceso completo a todos los recursos
- Gestionar usuarios, vehículos, turnos e inspecciones
- Eliminar registros
- Ver estadísticas completas

## Autenticación

El sistema utiliza **JWT (JSON Web Tokens)** para autenticación:

1. Registra un usuario en `/api/users/register`
2. Inicia sesión en `/api/users/login` para obtener el token
3. Incluye el token en el header de las peticiones protegidas:
   ```
   Authorization: Bearer <tu_token_jwt>
   ```

## Reglas de Negocio

### Estados de Turno
- **RESERVADO**: Turno creado, pendiente de confirmación
- **CONFIRMADO**: Turno confirmado, listo para inspección
- **COMPLETADO**: Inspección realizada
- **CANCELADO**: Turno cancelado

### Estados de Vehículo
- **ACTIVO**: Vehículo habilitado para inspecciones
- **INACTIVO**: Vehículo deshabilitado

### Resultados de Inspección
- **SEGURO**: 40 ≤ puntuación_total ≤ 80 Y todos los chequeos ≥ 5
- **RECHEQUEAR**: puntuación_total < 40 O algún chequeo < 5 (requiere observación obligatoria)

### Validaciones Importantes

1. **Turnos**:
   - Solo se pueden crear turnos para vehículos ACTIVOS
   - Los turnos deben ser en fechas futuras
   - Solo se pueden cancelar turnos en estado RESERVADO
   - Solo ADMIN e INSPECTOR pueden confirmar turnos

2. **Inspecciones**:
   - Solo se pueden inspeccionar turnos en estado CONFIRMADO
   - Las inspecciones deben realizarse el día programado del turno
   - Se requieren exactamente 8 chequeos (puntuación 1-10)
   - No se puede crear una inspección duplicada para el mismo turno
   - Si el resultado es RECHEQUEAR, la observación es obligatoria (min 10 caracteres)

3. **Vehículos**:
   - La matrícula es única en el sistema
   - El dueño debe existir y tener rol DUENIO

## Tecnologías Utilizadas

- **Flask**         - Framework web
- **SQLAlchemy**    - ORM para base de datos
- **Pydantic**      - Validación de datos
- **PyJWT**         - Autenticación JWT
- **MySQL**         - Base de datos
- **Pytest**        - Testing
- **flask-swagger** - Documentación Swagger/OpenAPI
