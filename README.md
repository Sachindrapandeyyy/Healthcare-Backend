# Healthcare Backend Enterprise API System

[![Healthcare Backend CI](https://github.com/Sachindrapandeyyy/Healthcare-Backend/actions/workflows/ci.yml/badge.svg)](https://github.com/Sachindrapandeyyy/Healthcare-Backend/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![DRF 3.18](https://img.shields.io/badge/django_rest_framework-3.18-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%2016-blue.svg)](https://www.postgresql.org/)
[![OpenAPI 3.0](https://img.shields.io/badge/OpenAPI-3.0%20Swagger-green.svg)](http://127.0.0.1:8000/api/docs/)

An enterprise-grade, HIPAA-aligned RESTful backend system for healthcare applications, built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, **JWT Authentication** (`djangorestframework-simplejwt`), and **OpenAPI 3.0** (`drf-spectacular`).

---

## 📌 Features & Architecture

### 1. Authentication & Session Security (`apps/accounts/`)
- Custom User Model using `email` as unique login identifier and `name`.
- JWT Token Authentication (`/api/auth/register/` and `/api/auth/login/`).
- **Token Blacklisting & Logout**: `/api/auth/logout/` invalidates refresh tokens on session termination.
- Password hashing with PBKDF2 SHA256 and strength validators.

### 2. Patient Management & Data Privacy (`apps/patients/`)
- Full CRUD operations with **owner-level isolation**: Users only have access to their own patients.
- **Healthcare Soft Deletes**: Medical records are never permanently hard-deleted; non-destructive archiving preserves audit trails for regulatory compliance.
- Input validation (valid age range, non-empty contacts, sanitized names).

### 3. Doctor Directory (`apps/doctors/`)
- Directory management with name, specialization, contact information, and experience.
- Email uniqueness validation and experience constraints.
- Soft-delete retention for medical staff history.

### 4. Patient-Doctor Assignment (`apps/mappings/`)
- Secure assignment of medical practitioners to patients.
- Duplicate mapping prevention (`unique_together` constraint).
- Cross-user assignment prevention (staff can only assign doctors to patients they own).

### 5. Enterprise Upgrades & API Capabilities
- 📖 **Interactive Swagger UI**: Interactive API testing at `/api/docs/` and Redoc at `/api/redoc/`.
- 🔍 **Pagination & Filtering**: Standard 10/20-item pagination, searchable by name/contact, filterable by gender and doctor specialization.
- 🛡️ **Rate Limiting / Throttling**: Brute-force protection on authentication and user rate limiting.
- 🌐 **CORS Headers**: Integrated `django-cors-headers` to support React, Next.js, and mobile clients.
- 🩺 **Health Check Probe**: `/api/health/` probe for Kubernetes, AWS ALB, and Docker liveness/readiness.
- 🐳 **Docker & Docker Compose**: Single-command containerized development with PostgreSQL 16 Alpine.
- ⚡ **CI/CD Pipeline**: Automated GitHub Actions workflow testing and verifying schema on every commit.

---

## 📁 Repository Structure

```text
healthcare_backend/
├── .github/workflows/ci.yml    # Automated GitHub Actions CI pipeline
├── Dockerfile                  # Multi-stage production container
├── docker-compose.yml          # Django + PostgreSQL 16 orchestration
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── postman_collection.json     # Ready-to-import Postman collection
├── healthcare_system/          # Core project configuration
│   ├── settings.py             # Settings (CORS, JWT, DRF, Database, Throttling)
│   ├── urls.py                 # Routing (OpenAPI, Health, Apps)
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── common/                 # Base models (SoftDelete), Pagination, Health check
    ├── accounts/               # Custom User, JWT Register, Login, Logout
    ├── patients/               # Patient CRUD, Filtering, Soft-delete
    ├── doctors/                # Doctor CRUD, Specialization filtering
    └── mappings/               # Patient-Doctor Mapping management
```

---

## 🚀 Quickstart Guide

### Option A: Running with Docker (Recommended)
Run the entire backend with PostgreSQL in one command:
```bash
docker compose up --build
```
The API is immediately available at `http://localhost:8000/api/docs/`.

---

### Option B: Local Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Sachindrapandeyyy/Healthcare-Backend.git
cd Healthcare-Backend
```

#### 2. Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### 3. Configure `.env`
Create `.env` (or copy from `.env.example`):
```ini
SECRET_KEY=your-secure-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# (Alternative for local standalone testing without PostgreSQL server):
# DB_ENGINE=django.db.backends.sqlite3

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
CORS_ALLOW_ALL_ORIGINS=True
```

#### 4. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

---

## 📖 API Documentation & Swagger UI

Open your browser to explore the interactive API:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI 3.0 Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- **Health Check**: [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/)

---

## 📡 API Endpoints Reference

All secured endpoints require the `Authorization: Bearer <token>` header.

### System & Diagnostics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health/` | Service health & database connectivity probe |
| `GET` | `/api/schema/` | Raw OpenAPI 3.0 YAML/JSON specification |
| `GET` | `/api/docs/` | Interactive Swagger UI documentation |
| `GET` | `/api/redoc/` | Interactive Redoc documentation |

### 1. Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register user with name, email, password | No |
| `POST` | `/api/auth/login/` | Obtain JWT access and refresh tokens | No |
| `POST` | `/api/auth/logout/` | Blacklist refresh token & terminate session | Yes |

### 2. Patient Management
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/patients/` | Add a new patient | Yes |
| `GET` | `/api/patients/?gender=Male&search=name` | List paginated patients (User-scoped) | Yes |
| `GET` | `/api/patients/<id>/` | Retrieve details of specific patient | Yes |
| `PUT` | `/api/patients/<id>/` | Update patient record | Yes |
| `DELETE` | `/api/patients/<id>/` | Soft-delete patient record | Yes |

### 3. Doctor Management
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor | Yes |
| `GET` | `/api/doctors/?specialization=Cardiology` | List paginated doctors (Search & Filter) | Yes |
| `GET` | `/api/doctors/<id>/` | Retrieve doctor details | Yes |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | Yes |
| `DELETE` | `/api/doctors/<id>/` | Soft-delete doctor record | Yes |

### 4. Patient-Doctor Mappings
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/mappings/` | Assign doctor to patient | Yes |
| `GET` | `/api/mappings/` | List all patient-doctor mappings | Yes |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to patient | Yes |
| `DELETE` | `/api/mappings/<id>/` | Remove doctor from patient | Yes |

---

## 🧪 Testing

Run the automated test suite across all 32 tests:
```bash
python manage.py test
```

---

## 📬 Postman Collection

Import `postman_collection.json` into Postman.
1. Send **Login User** request -> The JWT token is saved automatically to `{{access_token}}`.
2. All subsequent requests automatically use the token.
