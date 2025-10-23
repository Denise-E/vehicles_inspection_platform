# 📚 Documentación Swagger - Vehicle Inspection Platform API

## ✅ Implementación Completada

Se ha implementado la documentación completa de la API usando **flask-swagger** con una interfaz visual moderna usando **Swagger UI**.

---

## 🚀 Cómo Acceder a la Documentación

### Opción 1: Interfaz Visual (Recomendado)

Una vez que la aplicación esté corriendo:

```
http://localhost:5000/docs
```

Esta ruta muestra una interfaz amigable de Swagger UI donde puedes:
- ✅ Ver todos los endpoints organizados por tags
- ✅ Ver los esquemas de request y response
- ✅ Probar los endpoints directamente desde el navegador
- ✅ Autenticarte con JWT Bearer Token
- ✅ Ver ejemplos de uso

### Opción 2: Especificación JSON

Para obtener la especificación OpenAPI/Swagger en formato JSON:

```
http://localhost:5000/swagger
```

Este endpoint retorna la especificación completa que puede ser importada en herramientas como Postman, Insomnia, etc.

---

## 📖 Endpoints Documentados

### **Health** (1 endpoint)
- `GET /api/health` - Health check

### **Usuarios** (3 endpoints)
- `POST /api/users/register` - Registrar usuario (público)
- `POST /api/users/login` - Login y obtener JWT (público)
- `GET /api/users/profile/{user_id}` - Obtener perfil 🔒

### **Vehículos** (5 endpoints)
- `POST /api/vehicles/register/{duenio_id}` - Registrar vehículo 🔒
- `GET /api/vehicles/profile/{matricula}` - Obtener perfil 🔒
- `GET /api/vehicles` - Listar todos 🔒
- `PUT /api/vehicles/{matricula}` - Actualizar 🔒
- `PATCH /api/vehicles/{matricula}/desactivar` - Desactivar 🔒

### **Turnos** (8 endpoints)
- `POST /api/bookings/disponibilidad` - Consultar disponibilidad 🔒
- `POST /api/bookings/reservar` - Reservar turno 🔒
- `PUT /api/bookings/{id}/confirmar` - Confirmar turno 🔒
- `PUT /api/bookings/{id}/cancelar` - Cancelar turno 🔒
- `GET /api/bookings/{id}` - Obtener detalles 🔒
- `GET /api/bookings/usuario/{user_id}` - Listar por usuario 🔒
- `GET /api/bookings/vehiculo/{matricula}` - Listar por vehículo 🔒
- `GET /api/bookings` - Listar todos 🔒

🔒 = Requiere autenticación JWT

---

## 🔐 Cómo Usar la Autenticación en Swagger UI

### Paso 1: Registrar un usuario

1. Expandir `POST /api/users/register`
2. Hacer clic en "Try it out"
3. Completar el JSON de ejemplo:
```json
{
  "nombre_completo": "Tu Nombre",
  "mail": "tu@email.com",
  "telefono": "123456789",
  "contrasenia": "password123",
  "rol": "DUENIO"
}
```
4. Hacer clic en "Execute"

### Paso 2: Obtener el token JWT

1. Expandir `POST /api/users/login`
2. Hacer clic en "Try it out"
3. Completar con tus credenciales:
```json
{
  "mail": "tu@email.com",
  "contrasenia": "password123"
}
```
4. Copiar el valor del campo `"token"` de la respuesta

### Paso 3: Autenticarte en Swagger

1. Hacer clic en el botón **"Authorize"** (candado verde arriba a la derecha)
2. En el modal que aparece, pegar: `Bearer tu_token_aqui`
3. Hacer clic en "Authorize"
4. Hacer clic en "Close"

Ahora todos los endpoints protegidos funcionarán correctamente! 🎉

---

## 📊 Características de la Documentación

### ✅ Información Detallada

Cada endpoint incluye:
- **Descripción**: Qué hace el endpoint
- **Tag**: Categoría (Usuarios, Vehículos, Turnos)
- **Método HTTP**: GET, POST, PUT, PATCH
- **Seguridad**: Indica si requiere JWT
- **Parámetros**: Path params, query params, body
- **Schemas**: Estructura de request y response
- **Ejemplos**: Valores de ejemplo para cada campo
- **Respuestas**: Todos los códigos posibles (200, 201, 400, 401)
- **Modelos**: Esquemas de datos reutilizables

### ✅ Validaciones Documentadas

- **Tipos de datos**: string, integer, boolean, array, object
- **Formatos**: email, password, date, datetime
- **Restricciones**: minLength, maxLength, minimum, maximum, enum
- **Requeridos**: Campos obligatorios vs opcionales

### ✅ Seguridad JWT

- Configuración global de Bearer Token
- Identificación visual de endpoints protegidos
- Autenticación persistente durante la sesión

---

## 🛠️ Estructura de Archivos

```
src/
├── __init__.py                    # ✅ Configuración Swagger + rutas /swagger y /docs
├── routes/
│   ├── user_router.py            # ✅ Docstrings YAML completos
│   ├── vehicles_router.py        # ✅ Docstrings YAML completos
│   └── bookings_router.py        # ✅ Docstrings YAML completos
templates/
└── swagger.html                   # ✅ Interfaz visual Swagger UI
```

---

## 📝 Formato de Documentación

Flask-swagger usa docstrings con formato YAML especial. Ejemplo:

```python
@app.route("/ejemplo", methods=['POST'])
@token_required
def ejemplo():
    """
    Título descriptivo del endpoint
    ---
    tags:
      - Categoría
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            campo:
              type: string
              example: "valor ejemplo"
    responses:
      200:
        description: Éxito
        schema:
          type: object
          properties:
            resultado:
              type: string
      401:
        description: No autenticado
    """
    return {"resultado": "ok"}
```

---

## 🎨 Personalización

### Colores y Estilo

El archivo `templates/swagger.html` incluye un header personalizado con:
- Gradiente morado/azul corporativo
- Logo y título del proyecto
- Instrucciones de autenticación destacadas
- Diseño responsive

### Configuración Swagger UI

Parámetros configurables en `swagger.html`:
- `docExpansion: "none"` - Endpoints colapsados por defecto
- `filter: true` - Barra de búsqueda habilitada
- `tryItOutEnabled: true` - Botón "Try it out" siempre visible
- `persistAuthorization: true` - Guarda el token en localStorage

---

## 🚫 Solución de Problemas

### Error: "Template not found"

**Problema**: Flask no encuentra `swagger.html`

**Solución**: Asegurar que la carpeta `templates/` esté en la raíz del proyecto (mismo nivel que `src/`)

```
vehicles_inspection_platform/
├── templates/
│   └── swagger.html
├── src/
│   └── __init__.py
└── app.py
```

### Error: "swagger is not defined"

**Problema**: Falta instalar flask-swagger

**Solución**:
```bash
pip install flask-swagger==0.2.14
```

### Los endpoints no aparecen

**Problema**: Los docstrings no tienen el formato correcto

**Solución**: Verificar que:
1. El docstring tenga `"""` al inicio y final
2. Haya un `---` después del título
3. La indentación sea correcta (2 espacios por nivel)

---

## 📦 Exportar Documentación

### Para Postman

1. Ir a `http://localhost:5000/swagger`
2. Copiar todo el JSON
3. En Postman: Import → Raw text → Pegar JSON → Import

### Para README

El JSON de `/swagger` puede ser usado para generar documentación markdown automáticamente con herramientas como:
- [swagger-markdown](https://www.npmjs.com/package/swagger-markdown)
- [widdershins](https://github.com/Mermade/widdershins)

---

## ✨ Mejoras Futuras

Ideas para extender la documentación:

1. **Agregar ejemplos de respuesta reales**: Mostrar JSONs de ejemplo más completos
2. **Documentar códigos de error específicos**: 404, 409, 422, etc.
3. **Agregar webhooks**: Si se implementan notificaciones
4. **Versionamiento**: Documentar múltiples versiones de la API
5. **Rate limiting**: Documentar límites de requests

---

## 📚 Referencias

- [Flask-Swagger GitHub](https://github.com/gangverk/flask-swagger)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [YAML Syntax](https://yaml.org/spec/1.2.2/)

---

## 🎓 Justificación para Defensa Académica

### ¿Por qué Swagger/OpenAPI?

1. **Estándar de la industria**: OpenAPI es el estándar más usado para documentar APIs REST
2. **Autodocumentación**: La documentación vive con el código (docstrings)
3. **Interactivo**: Los evaluadores pueden probar la API sin Postman
4. **Profesional**: Demuestra madurez del proyecto
5. **Mantenible**: Documentación y código sincronizados

### Decisiones de diseño:

- **flask-swagger**: Ligero, integración nativa con Flask
- **Swagger UI**: Interfaz estándar, conocida universalmente
- **Organización por tags**: Facilita navegación (Usuarios, Vehículos, Turnos)
- **Ejemplos completos**: Reduce fricción para probar la API
- **Seguridad documentada**: JWT claramente indicado en cada endpoint

---

**¡Documentación completa y lista para la defensa!** 🎉

