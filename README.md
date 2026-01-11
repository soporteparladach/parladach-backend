# Parladach Backend

Backend del proyecto **Parladach**, desarrollado con **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0** y **Alembic**.

Este README está orientado **únicamente a desarrollo**.

---

## Requisitos

- Python 3.11+
- PostgreSQL 17
- Git
- (Opcional) Docker — se usará más adelante

---

## Levantar el backend (desarrollo local)

### 1. Crear entorno virtual

```bash
python -m venv .venv
```

Activar:

- Windows (PowerShell / Git Bash):
```bash
.venv/Scripts/activate
```

- Linux / macOS:
```bash
source .venv/bin/activate
```

---

### 2. Instalar dependencias

Desde la carpeta `backend/`:

```bash
pip install -e ".[dev]"
```

---

### 3. Configurar variables de entorno

Crear archivo `.env` en `backend/`:

```env
APP_ENV=local
DATABASE_URL=postgresql+psycopg://postgres:admin@localhost:5432/parladach
# JWT / Auth
SECRET_KEY=CHANGE_ME_SUPER_SECRET_LOCAL
ACCESS_TOKEN_EXPIRES_MINUTES=60
JWT_ALGORITHM=HS256
# Admin (creación controlada)
ADMIN_EMAIL=admin@parladach.com
ADMIN_PASSWORD=Admin123*
```

Referencia: `.env.example`

---

### 4. Levantar el servidor

```bash
uvicorn app.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

Verificar:
```
http://localhost:8000/health
```

---

## Estructura del proyecto

```text
backend/
├── alembic/                # Migraciones
├── scripts/                # Scripts manuales (seed, utilidades)
├── src/
│   └── app/
│       ├── api/            # Routers FastAPI
│       ├── config/         # Settings y variables de entorno
│       ├── core/           # Infraestructura transversal
│       ├── models/         # Modelos ORM
│       └── main.py         # Punto de entrada
├── tests/                  # Tests
├── pyproject.toml
└── README.md
```

---

## Migraciones (Alembic)

Crear migración:

```bash
alembic revision --autogenerate -m "descripcion"
```

Ejecutar migraciones:

```bash
alembic upgrade head
```

---

## Seed de usuarios (solo desarrollo)

```bash
python scripts/seed_users.py
```

Crea usuarios:
- ADMIN
- STUDENT
- TEACHER

---

## Sprint 1 — Auth (registro, login, sesión, RBAC)

Esta sección documenta el flujo mínimo de autenticación implementado en el Sprint 1.

---

### Endpoints de Auth

Base: `/auth`

#### Registro (solo STUDENT / TEACHER)

**POST** `/auth/register`

```json
{
  "email": "student@example.com",
  "password": "Student123*",
  "role": "STUDENT"
}
```

Respuesta:

```json
{
  "user": {
    "id": 1,
    "email": "student@example.com",
    "role": "STUDENT",
    "status": "ACTIVE",
    "created_at": "2026-01-11T12:34:56Z"
  }
}
```

---

#### Login (email + password)

**POST** `/auth/login`

```json
{
  "email": "student@example.com",
  "password": "Student123*"
}
```

Respuesta:

```json
{
  "access_token": "JWT_AQUI",
  "token_type": "bearer"
}
```

- Credenciales inválidas → `401`
- Usuario `SUSPENDED/DELETED/INACTIVE` → `401` genérico

---

#### Mi sesión

**GET** `/auth/me`

Header:

```
Authorization: Bearer <access_token>
```

Respuesta:

```json
{
  "id": 1,
  "email": "student@example.com",
  "role": "STUDENT",
  "status": "ACTIVE",
  "created_at": "2026-01-11T12:34:56Z"
}
```

- Sin token → `401`
- Usuario bloqueado → `403`

---

## RBAC — Dashboards placeholder

Endpoints protegidos por rol:

- **GET** `/student/dashboard` → STUDENT
- **GET** `/teacher/dashboard` → TEACHER
- **GET** `/admin/dashboard` → ADMIN

Comportamiento:
- Sin token → `401`
- Rol incorrecto → `403`

---

## Crear ADMIN (controlado)

No existe endpoint público para crear ADMIN.

Usar script:

```bash
python scripts/create_admin.py
```

Requiere variables:

```env
ADMIN_EMAIL
ADMIN_PASSWORD
```

---

## Tests

```bash
pytest -q
```

Los tests cubren:
- Registro
- Login
- Protección por token
- RBAC por rol
- Bloqueo por estado de usuario

---

## Notas

- No hay autenticación aún (ETAPA 1)
- Solo existe `/health`
- Docker y despliegue se introducirán en etapas posteriores


