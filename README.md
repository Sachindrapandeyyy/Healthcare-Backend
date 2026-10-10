# Healthcare Backend API System

A secure, scalable RESTful backend system for managing healthcare records, built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT Authentication** (`djangorestframework-simplejwt`).

---

## 📌 Project Overview

This backend system enables authenticated healthcare staff and users to:
1. **User Authentication**: Register and log in securely with JWT token authentication (Access & Refresh tokens).
2. **Patient Management**: Securely create, view, update, and delete patient records. Patients are strictly scoped to the authenticated user who created them.
3. **Doctor Management**: Manage medical practitioner directory and specialties.
4. **Patient-Doctor Mapping**: Assign doctors to patients, view doctors assigned to a patient, list all mappings, and unassign doctors.
5. **Security & Validation**: Standardized error handling, input validation, unique constraints, and environment-based configuration.

---

## 🛠 Tech Stack

- **Framework**: Django 6.0+
- **API Toolkit**: Django REST Framework (DRF) 3.18+
- **Authentication**: `djangorestframework-simplejwt`
- **Database**: PostgreSQL (via `psycopg` v3 driver) with SQLite fallback option
- **Configuration**: `python-dotenv`

---

## 📁 Project Structure

```text
healthcare_backend/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
├── postman_collection.json
├── healthcare_system/          # Core Project Configuration
│   ├── __init__.py
│   ├── settings.py             # Settings, JWT config, PostgreSQL setup
│   ├── urls.py                 # Top-level API routing
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── common/                 # Shared utilities, custom exception handler, E2E tests
    │   ├── exceptions.py
    │   └── test_e2e_flow.py
    ├── accounts/               # Custom User & JWT Auth
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests.py
    ├── patients/               # Patient CRUD & Owner Scoping
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests.py
    ├── doctors/                # Doctor CRUD
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests.py
    └── mappings/               # Patient-Doctor Mapping
        ├── models.py
        ├── serializers.py
        ├── views.py
        ├── urls.py
        └── tests.py
```

---

## ⚙️ Installation & Setup

### 1. Clone or Open the Repository
```bash
cd C:\Users\Sachi\.gemini\antigravity\scratch\healthcare_backend
```

### 2. Set Up Virtual Environment (Optional / Recommended)
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory (or copy `.env.example`):
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

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
```

### 5. Create PostgreSQL Database (if using PostgreSQL)
In PostgreSQL / `psql`:
```sql
CREATE DATABASE healthcare_db;
```

### 6. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## 🧪 Running Automated Tests

Run the complete test suite covering all 29 tests (models, views, serializers, permissions, and end-to-end integration flows):

```bash
python manage.py test
```

To run tests for individual apps:
```bash
python manage.py test apps.accounts
python manage.py test apps.patients
python manage.py test apps.doctors
python manage.py test apps.mappings
python manage.py test apps.common
```

---

## 📡 API Endpoints Documentation

All requests except registration and login require the `Authorization` header:
```http
Authorization: Bearer <your_access_token>
```

### 1. Authentication APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user with name, email, password | No |
| `POST` | `/api/auth/login/` | Authenticate user & return JWT tokens | No |

#### `POST /api/auth/register/`
**Request Body:**
```json
{
  "name": "John Doe",
  "email": "johndoe@example.com",
  "password": "SecurePassword123!"
}
```
**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "johndoe@example.com",
    "date_joined": "2026-10-10T11:00:00Z"
  }
}
```

#### `POST /api/auth/login/`
**Request Body:**
```json
{
  "email": "johndoe@example.com",
  "password": "SecurePassword123!"
}
```
**Response (200 OK):**
```json
{
  "message": "Login successful",
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "johndoe@example.com"
  }
}
```

---

### 2. Patient Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/patients/` | Add a new patient (assigned to request user) | Yes |
| `GET` | `/api/patients/` | Retrieve all patients created by authenticated user | Yes |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient | Yes |
| `PUT` | `/api/patients/<id>/` | Update patient details | Yes |
| `DELETE` | `/api/patients/<id>/` | Delete a patient record | Yes |

#### `POST /api/patients/`
**Request Body:**
```json
{
  "name": "Alice Wonderland",
  "age": 32,
  "gender": "Female",
  "contact_number": "+1-555-0199",
  "address": "123 Health Ave, Medical City",
  "medical_history": "No known allergies"
}
```
**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Alice Wonderland",
  "age": 32,
  "gender": "Female",
  "contact_number": "+1-555-0199",
  "address": "123 Health Ave, Medical City",
  "medical_history": "No known allergies",
  "created_by": 1,
  "created_by_email": "johndoe@example.com",
  "created_by_name": "John Doe",
  "created_at": "2026-10-10T11:05:00Z",
  "updated_at": "2026-10-10T11:05:00Z"
}
```

---

### 3. Doctor Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor | Yes |
| `GET` | `/api/doctors/` | Retrieve all doctors | Yes |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | Yes |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | Yes |
| `DELETE` | `/api/doctors/<id>/` | Delete a doctor record | Yes |

#### `POST /api/doctors/`
**Request Body:**
```json
{
  "name": "Dr. Gregory House",
  "specialization": "Diagnostic Medicine",
  "phone": "+1-555-0987",
  "email": "house@princeton.org",
  "experience_years": 20
}
```
**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Dr. Gregory House",
  "specialization": "Diagnostic Medicine",
  "phone": "+1-555-0987",
  "email": "house@princeton.org",
  "experience_years": 20,
  "created_at": "2026-10-10T11:10:00Z",
  "updated_at": "2026-10-10T11:10:00Z"
}
```

---

### 4. Patient-Doctor Mapping APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/mappings/` | Assign a doctor to a patient | Yes |
| `GET` | `/api/mappings/` | Retrieve all patient-doctor mappings | Yes |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient | Yes |
| `DELETE` | `/api/mappings/<id>/` | Remove a doctor from a patient (by mapping ID) | Yes |

#### `POST /api/mappings/`
**Request Body:**
```json
{
  "patient": 1,
  "doctor": 1,
  "notes": "Assigned for diagnostic workup"
}
```
**Response (201 Created):**
```json
{
  "id": 1,
  "patient": {
    "id": 1,
    "name": "Alice Wonderland",
    "age": 32,
    "gender": "Female",
    "contact_number": "+1-555-0199"
  },
  "doctor": {
    "id": 1,
    "name": "Dr. Gregory House",
    "specialization": "Diagnostic Medicine",
    "phone": "+1-555-0987",
    "email": "house@princeton.org",
    "experience_years": 20
  },
  "assigned_date": "2026-10-10T11:15:00Z",
  "notes": "Assigned for diagnostic workup"
}
```

#### `GET /api/mappings/<patient_id>/`
Returns all doctors assigned to patient `<patient_id>`.

#### `DELETE /api/mappings/<id>/`
Deletes the mapping record with ID `<id>`.
**Response (200 OK):**
```json
{
  "message": "Doctor removed from patient successfully."
}
```

---

## 📬 Postman Testing

A ready-to-import Postman Collection is included at:
`healthcare_backend/postman_collection.json`

### To use in Postman:
1. Open Postman -> Click **Import** -> Select `postman_collection.json`.
2. Run the **Login User** request. The test script will automatically extract and set the `{{access_token}}` variable.
3. All subsequent requests (Patients, Doctors, Mappings) will automatically inherit the token!
