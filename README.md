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

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### 2. Installation
```bash
# Clone the repository and navigate to the directory
pip install -r requirements.txt
```

### 3. Configuration
Configure your secrets and database URLs in the `.env` file. The system requires two unique secrets:
- `SECRET_KEY_ACCESS`: For access tokens.
- `SECRET_KEY_REFRESH`: For refresh tokens.

### 4. Execution
```bash
# Start the asynchronous server
uvicorn app.main:app --reload
```

---

## 🧪 Testing & Verification

### Interactive Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Validation Client
Open `frontend/index.html` in your browser to access the **Premium Dashboard**. This allows you to visually test the full registration, login, rotation, and revocation lifecycle.

### Automated Suites
```bash
pytest tests/ --asyncio-mode=auto
```

---

## 📄 License
Confidential // Project Core-Auth Spec v1.4.2
