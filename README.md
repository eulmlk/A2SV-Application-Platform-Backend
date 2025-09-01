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

### 4. Configure Environment Variables

This step creates a local configuration file that tells your application how to connect to the database and what secret keys to use for security. This information is stored in a .env file, which is kept private and is never committed to version control.

#### 4.1. Create a New .env File

In the root directory of your project, create a new, empty file and name it exactly `.env`.

You can do this using your code editor (File -> New File) or with a terminal command:

- On macOS and Linux:

```bash
touch .env
```

- On Windows (Command Prompt):

```bash
type nul > .env
```

#### 4.2. Add the Required Configuration Template

Open your new, empty .env file and paste the following content into it. This will serve as your template.

```env
# Your PostgreSQL connection string
DATABASE_URL=postgresql://user:password@localhost:5432/a2sv_app

# Generate a strong secret key for JWT
JWT_SECRET_KEY=your_super_secret_jwt_key

# Standard JWT settings
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### 4.3. Update the Configuration Values

You must now replace the placeholder values in the file with your actual local settings.

`DATABASE_URL`: This is the connection string for your PostgreSQL database. Replace user, password, and potentially a2sv_app with the details of your own PostgreSQL instance.

- `user`: Your PostgreSQL username (often postgres by default).
- `password`: The password you set for that user.
- `localhost:5432`: This is usually correct if your database is running on your local machine.
- `a2sv_app`: The name of the database you want to connect to. Make sure this database exists on your server.

`JWT_SECRET_KEY`: This is a critical security value. You must replace the placeholder text with a long, random, and secret string. This key is used to sign your authentication tokens.

- You can generate a strong key easily by running the following command in your terminal (for windows run it using Git Bash not Command Prompt or Powershell):

```bash
openssl rand -hex 32
```

Copy the long string of text it outputs and paste it as the value for `JWT_SECRET_KEY`.

Other Variables
The remaining variables (`JWT_ALGORITHM`, etc.) have sensible defaults that you typically do not need to change for local development.

After editing, your `.env` file might look something like this:

```env
DATABASE_URL="postgresql://postgres:my-secret-pg-password@localhost:5432/a2sv_app"
JWT_SECRET_KEY="d4e1f8a7b3c2d5f6e8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1"
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Save the changes to your .env file. The application is now configured to connect to your database and handle security correctly.

#### 5. Set Up the Database

This project uses Alembic to manage database schema migrations. After configuring your `DATABASE_URL`, run the following command to apply all migrations and create the necessary tables in your database.

```bash
alembic upgrade head
```

#### 6. Run the Application

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
