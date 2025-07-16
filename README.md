# A2SV Application Platform Backend

## Overview

This is the backend implementation for the A2SV Application Platform MVP, following Clean Architecture principles with FastAPI, SQLAlchemy, and PostgreSQL. The project includes JWT-based authentication, role-based access control (RBAC), and a versioned database schema managed by Alembic.

## Project Structure

```
app/
  api/           # FastAPI routers, dependencies, and endpoint logic
  core/          # Core logic: settings, security, database sessions
  domain/        # Pure business entities (User, Application, etc.)
  usecases/      # Usecase classes (high-level business logic)
  repositories/  # Data access layer: interfaces & SQLAlchemy implementations
  models/        # SQLAlchemy models (DB table definitions)
  schemas/       # Pydantic models (request/response validation)
  main.py        # FastAPI application entrypoint
migrations/      # Alembic database migration scripts
alembic.ini      # Alembic configuration file
requirements.txt # Python dependencies
README.md        # Project documentation
```

## Setup and Installation

Follow these steps to set up your local development environment.

### 1. Prerequisites

- Python 3.10+
- PostgreSQL server running locally or accessible.

### 2. Clone the Repository and Set Up Virtual Environment

Follow these steps to get the project code onto your local machine and create an isolated environment for its dependencies.

#### 2.1. Clone the Project with Git

Navigate to the directory where you want to store the project. Use the git clone command to download the repository code. You can find the repository URL on the main page of the project's GitLab or GitHub page.

```bash
git clone https://github.com/eulmlk/A2SV-Application-Platform-Backend.git
```

#### 2.2. Navigate into the Project Directory

The clone command creates a new folder named after the repository. You must move into this folder.

```bash
cd A2SV-Application-Platform-Backend
```

#### 2.3. Create a Python Virtual Environment

This creates a self-contained "bubble" for your project's Python packages, preventing conflicts with other projects. We will name the environment venv.

```bash
python -m venv venv
```

#### 2.4. Activate the Virtual Environment

This is a crucial step that tells your terminal to use the Python and Pip executables from within the venv folder. The command is different for different operating systems.

- On macOS and Linux:

```bash
source venv/bin/activate
```

- On Windows (Command Prompt or PowerShell):

```cmd
venv\Scripts\activate
```

### 3. Install Dependencies

Install all required Python packages from the requirements.txt file.

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

This project uses Alembic to manage database schema migrations. After configuring your `DATABASE_URL`, run the following command to apply all migrations and create the necessary tables in your database.

```bash
alembic upgrade head
```

### 5. Run the Application

You can now start the FastAPI development server.

```bash
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000/docs.

## Database Migrations (Alembic)

Alembic is used to handle all changes to the database schema. If you are contributing to the project and need to make a change to the database models:

Modify the SQLAlchemy model files in `app/models/`.

Generate a new migration script automatically:

```bash
alembic revision --autogenerate -m "A short description of the change"
```

Review the generated script in `migrations/versions/` to ensure it's correct.

Apply the changes to your local database to test them:

```bash
alembic upgrade head
```

Commit the new migration script to version control along with your model changes.
