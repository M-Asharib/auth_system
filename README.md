# Advanced Asynchronous Backend System (Enterprise Core)
### v1.4.2-Prod Compliance Framework

A high-performance, non-blocking asynchronous security and user routing engine built with **FastAPI**. This system implements a Zero-Trust architecture with a stateless/stateful hybrid model.

---

## 🚀 Key Features

- **Asynchronous Execution**: Fully non-blocking I/O using `FastAPI`, `SQLAlchemy` (Async), and `Redis` (Async).
- **Dual-Token Security**: Short-lived **Access Tokens** and long-lived **Refresh Tokens** signed with unique cryptographic secrets.
- **Stateful Token Revocation**: Instant session invalidation via a fast **Redis** memory layer (Blacklisting).
- **Zero-Trust Dependency Injection**: Automated token validation and blacklist checking for every protected route.
- **Premium Apple-Style UI**: A sleek, glassmorphism-inspired validation client for end-to-end testing.
- **Quality Gate**: Integrated GitHub Actions pipeline with Linting (Ruff), SAST (Bandit), and Integration Suites.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy 2.0 (Async)](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- **Cache/Blacklist**: [Redis](https://redis.io/)
- **Security**: PyJWT, Passlib (Bcrypt)
- **Validation**: Pydantic v2
- **Testing**: Pytest, Httpx

---

## 📂 Project Structure

```text
├── .github/workflows/      # CI/CD Pipeline (GitHub Actions)
├── app/
│   ├── api/                # API Routers & Dependencies
│   ├── core/               # Security & Configuration
│   ├── db/                 # Session & Base Models
│   ├── models/             # SQLAlchemy Database Models
│   ├── schemas/            # Pydantic JSON Schemas
│   ├── services/           # Redis & External Services
│   └── main.py             # Application Entry Point
├── frontend/               # Apple-style Validation Client
├── tasks/                  # Implementation Roadmap & TODOs
├── tests/                  # Asynchronous Integration Suites
├── .env                    # Environment Configuration
└── requirements.txt        # Project Dependencies
```

---

## 🚦 Quick Start Guide

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.11+**
- **Redis Server** (Required for token blacklisting)
- **PostgreSQL** (Optional, defaults to SQLite for local development)

### 2. Installation
Clone the repository and install dependencies using a virtual environment:

```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the example environment file and update it with your secrets:

```bash
cp .env.example .env
```
*Note: Make sure to generate strong secrets for `SECRET_KEY_ACCESS` and `SECRET_KEY_REFRESH`. You can use `openssl rand -hex 32` for this.*

### 4. Running the System
Start the FastAPI server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

### 5. Accessing the Application
Once the server is running, you can access the various components:
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Validation Client (Frontend)**: [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)
- **Root API Endpoint**: [http://localhost:8000/](http://localhost:8000/)


---

## 🧪 Testing & Verification

### Interactive Documentation
Explore the API endpoints directly through the browser:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Validation Client (Frontend)
The system serves a premium glassmorphism-inspired UI at [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html). Use this to visually test:
- User Registration & Password Hashing
- Secure Login & Dual-Token Issuance
- Automatic Token Rotation
- Stateful Logout (Redis Blacklisting)


### Automated Suites
```bash
pytest tests/ --asyncio-mode=auto
```

---

## 📄 License
Confidential // Project Core-Auth Spec v1.4.2
