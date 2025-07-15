# A2SV Application Platform Backend

## Overview
This is the backend implementation for the A2SV Application Platform MVP, following Clean Architecture principles with FastAPI, SQLAlchemy, and PostgreSQL.

## Project Structure
```
app/
  api/           # FastAPI routers, dependencies, JWT, RBAC
  core/          # Settings, security, utils
  domain/        # Entities (User, Application, etc.)
  usecases/      # Usecase classes (business logic)
  repositories/  # Interfaces & SQLAlchemy implementations
  models/        # SQLAlchemy models (DB tables)
  schemas/       # Pydantic models (request/response)
  main.py        # FastAPI app entrypoint
migrations/      # Alembic migrations (optional)
.env             # Environment variables
requirements.txt # Python dependencies
README.md        # Project documentation
```

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root with the following variables:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/a2sv_app
   JWT_SECRET_KEY=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```
3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database
- Uses PostgreSQL. Update `DATABASE_URL` in `.env` as needed.

## Authentication
- JWT-based authentication with access and refresh tokens.

## RBAC
- Role-based access control enforced via FastAPI dependencies.
