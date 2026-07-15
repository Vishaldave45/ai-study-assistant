# AI Study Assistant 🎓

A modern web application featuring an AI-powered study assistant with a FastAPI backend and a frontend.

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic
- **Package Manager & Workflow**: [uv](https://github.com/astral-sh/uv) (for lightning-fast dependency management, virtual environments, and workspace orchestration)
- **Frontend**: *Under construction* (located in `frontend/`)

---

## 🚀 Quick Start & Environment Setup

This project uses `uv` workspaces to manage dependencies. The workspace root is configured to orchestrate Python projects in subdirectories like `backend/`.

### 1. Prerequisites
Make sure you have `uv` installed. If you don't have it, install it via:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Synchronization & Dependencies
To install all workspace dependencies and synchronize your virtual environment:
```bash
# Sync dependencies (creates or updates the root `.venv`)
uv sync
```

*Note: Since the backend is a workspace member, `uv sync` automatically installs backend dependencies into the root `.venv`.*

### 3. Environment Variables
Copy the example environment file and configure your settings:
```bash
cp .env.example backend/app/.env
```
Open `backend/app/.env` and update the `DATABASE_URL` and `GEMINI_API_KEY` as needed.

---

## 💻 Running the Backend

All Python commands should be run using `uv run` to ensure they run inside the correct workspace environment.

### Start the FastAPI Dev Server
To start the backend with live reloading:
```bash
# Run uvicorn server
uv run --project backend uvicorn app.main:app --reload
```
The API will be available at: http://localhost:8000
Interactive docs (Swagger UI) at: http://localhost:8000/docs

### Run Database Migrations
We use Alembic for managing database schemas.
```bash
# Run all migrations up to the latest revision
uv run --project backend alembic upgrade head

# Generate a new migration revision automatically (after modifying models)
uv run --project backend alembic revision --autogenerate -m "Add new table"
```

### Test Database Connection
You can run a quick check to verify the database connection:
```bash
uv run --project backend python backend/test_db.py
```

---

## 📂 Project Structure

```
├── .venv/                 # Shared virtual environment managed by uv
├── alembic/               # Root migration folder (unused)
├── backend/               # Python FastAPI backend
│   ├── alembic/           # Active database migrations
│   ├── alembic.ini        # Alembic configuration
│   ├── app/               # Main FastAPI application package
│   │   ├── api/           # API endpoints (v1, etc.)
│   │   ├── core/          # App settings and configs
│   │   ├── database/      # Session setup and models
│   │   ├── repositories/  # Database access patterns
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── security/      # Auth and hashing utils
│   │   ├── services/      # Business logic services
│   │   ├── main.py        # Backend entrypoint
│   │   └── .env           # Backend runtime environment configuration
│   ├── pyproject.toml     # Backend dependency configuration
│   └── requirements.txt   # Legacy requirements file (for reference)
├── frontend/              # Frontend files (under construction)
├── pyproject.toml         # Root workspace configuration
└── README.md              # Project documentation (this file)
```
