# vehicles_inspection_platform
University integrative project – vehicle inspection booking &amp; safety evaluation system built with Python and Flask.

## Requisitos

- Python 3.11
- pip (Administrador de paquetes de Python)

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

### Documentación

La documentación del proyecto está disponible en la ruta /swagger. Puedes acceder a ella navegando a http://localhost:5000/swagger una vez que el servidor esté en funcionamiento.