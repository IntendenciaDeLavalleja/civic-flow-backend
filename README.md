# Agil Proyect Management Software - APMS – Backend

Backend REST desarrollado con Flask, SQLAlchemy, Flask-JWT-Extended y Flask-Migrate.

## Stack

| Capa | Tecnología |
|---|---|
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy + Alembic |
| Auth | Flask-JWT-Extended (JWT + 2FA por email) |
| DB | MariaDB / SQLite (desarrollo) |
| Archivos | Almacenamiento local del servidor |

## Estructura

```
backend/
  app/
    api/          # Blueprints REST: auth, users, units, projects, tasks, works, admin
    models/       # Modelos ORM: User, Unit, Project, Task, Work, ActivityLog …
    services/     # email_service
    utils/        # Helpers de logging
    config.py     # Configuración desde variables de entorno
    extensions.py # db, migrate, mail, jwt, limiter
```

## Setup

### 1. Entorno virtual

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Variables de entorno

Copiar `.env.example` a `.env` y completar:

```env
SECRET_KEY=cambiar-en-produccion
JWT_SECRET_KEY=cambiar-en-produccion
DATABASE_URL=mysql+mariadb://user:pass@localhost/gvl_db
MAIL_SERVER=smtp.ejemplo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@ejemplo.com
MAIL_PASSWORD=
APP_NAME=Agil Proyect Management Software - APMS
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
WORKS_UPLOAD_DIR=./uploads/works
```

### 4. Inicializar base de datos

```bash
flask db upgrade
# O bien, para desarrollo rápido sin Alembic:
flask init-db
```

### 5. Crear super-administrador inicial

```bash
flask create-admin "Nombre Apellido" admin@ejemplo.com ContraseniaSegura true
```

### 6. Datos de demo (opcional)

```bash
flask seed-demo
# Para regenerar:
flask seed-demo --force
```

### 7. Levantar el servidor

Desarrollo:
```bash
flask run
```

Producción:
```bash
gunicorn wsgi:app -w 4 -b 0.0.0.0:5000
```

## API – Resumen de endpoints

| Método | Ruta | Descripción | Rol mínimo |
|--------|------|-------------|------------|
| POST | `/api/auth/login` | Login paso 1 (credenciales) | público |
| POST | `/api/auth/verify-2fa` | Login paso 2 (código 2FA) | pending_token |
| GET | `/api/auth/me` | Perfil propio | user |
| POST | `/api/auth/logout` | Logout | user |
| PUT | `/api/auth/change-password` | Cambiar contraseña propia | user |
| GET | `/api/users` | Listar usuarios | admin |
| POST | `/api/users` | Crear usuario | admin |
| PUT | `/api/users/:id` | Actualizar usuario | admin / self |
| DELETE | `/api/users/:id` | Desactivar usuario | admin |
| PUT | `/api/users/:id/reset-password` | Resetear contraseña | admin |
| GET | `/api/units` | Listar unidades/áreas | user |
| POST | `/api/units` | Crear unidad | admin |
| PUT | `/api/units/:id` | Actualizar unidad | admin |
| DELETE | `/api/units/:id` | Eliminar unidad | admin |
| GET | `/api/projects` | Listar proyectos | user |
| POST | `/api/projects` | Crear proyecto | user |
| PUT | `/api/projects/:id` | Actualizar proyecto | user |
| DELETE | `/api/projects/:id` | Eliminar proyecto | admin |
| GET | `/api/tasks` | Listar tareas | user |
| POST | `/api/tasks` | Crear tarea | user |
| PUT | `/api/tasks/:id` | Actualizar tarea | user |
| PATCH | `/api/tasks/:id/status` | Cambiar estado tarea | user |
| DELETE | `/api/tasks/:id` | Eliminar tarea | user |
| GET | `/api/works` | Listar procesos/obras | user |
| GET/POST | `/api/works/:id/documents` | Documentos de proceso | user |
| GET/POST | `/api/works/:id/tasks` | Tareas de proceso | user |
| GET | `/api/works/:id/kpis` | KPIs de proceso | user |
| GET | `/api/admin/dashboard` | Panel resumen | admin |
| GET | `/api/admin/logs` | Auditoría de acciones | **super_admin** |
| GET | `/api/admin/export/projects` | Exportar CSV | admin |
| GET | `/api/admin/export/tasks` | Exportar CSV | admin |

## Roles

| Rol | Descripción |
|-----|-------------|
| `super_admin` | Acceso completo + auditoría |
| `admin` | Gestión de usuarios, áreas, proyectos y tareas |
| `user` | Acceso a su propia área |


```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar y renombrar el archivo de ejemplo:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Editar el archivo `.env` con tus credenciales de base de datos, correo y MinIO.

Variables Redis soportadas:

- `REDIS_URL` (opcional, tiene prioridad si se define).
- `REDIS_HOST` (default `redis`).
- `REDIS_PORT` (default `6379`).
- `REDIS_DB` (default `0`).
- `REDIS_PASSWORD` (opcional).

Si usas password en Redis y no defines `REDIS_URL`, la app construye automáticamente:
`redis://:PASSWORD@HOST:PORT/DB`

### 4. Inicializar Base de Datos

Asegurate de que MariaDB esté corriendo y la base de datos `buzon_db` (o la que hayas puesto en .env) exista.

```bash
# Inicializar migraciones (solo la primera vez si no existe carpeta migrations)
flask db init

# Generar script de migración inicial
flask db migrate -m "Initial migration"

# Aplicar cambios a la DB
flask db upgrade
```

Si actualizás desde una versión anterior, ejecutá siempre `flask db upgrade` antes de iniciar la app para evitar errores de columnas faltantes en `pre_reservations` (por ejemplo `archive_reason`, `checked_in_at`, `completed_at`).

### 5. Correr en modo desarrollo
Activar entorno:
```bash
venv\Scripts\activate
```

```bash
flask run
# O usando wsgi.py directamente
python wsgi.py
```

## Rutas y Acceso

El sistema está dividido en dos interfaces principales:

1.  **Tablero Web (Admin Flask)**: 
    - URL: `/admin/`
    - Autenticación: `/admin/login` (Basada en Sesiones y Captcha).
    - Uso: Gestión de trámites, locales y agenda desde el navegador.

2.  **App de Escritorio (Electron)**:
    - Autenticación: `/api/auth/login` (Basada en JSON).
    - Uso: Operaciones administrativas remotas desde la aplicación Electron.

## Comandos útiles

- `flask routes`: Ver todas las rutas registradas.
- `flask db upgrade`: Aplicar migraciones pendientes.

### Comandos Personalizados (CLI)

1.  **Crear Usuario Administrador**:
    Crea un admin (o super admin) con username, email, password y flag.
    ```bash
    flask create-admin nombre-de-admin mail-de-admin contraseña-de-admin true/false-super-admin
    ```

2.  **Inicializar Bucket MinIO**:
    Verifica que la conexión a MinIO funcione y crea el bucket si no existe.
    ```bash
    flask init-bucket
    ```

3.  **Generar Secret Key**:
    Genera un token seguro para pegar en tu `.env`.
    ```bash
    flask rotate-secret
    ```

## Testing

```bash
pytest
```
