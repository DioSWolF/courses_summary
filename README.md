# FastAPI + Celery + PostgreSQL + Redis Project

This repository contains a FastAPI application with Celery workers for asynchronous tasks, using PostgreSQL as the database and Redis as the message broker and rate limiter storage.

---

## Features

- REST API built with FastAPI
- Asynchronous task processing with Celery
- PostgreSQL database for data persistence
- Redis for caching and Celery broker
- Dockerized for easy deployment and development

---

## Prerequisites

- Docker
- Docker Compose

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/DioSWolF/courses_summary.git
cd courses_summary
```

### Environment Variables

Create a \`.env\` file in the project root with your configuration. Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

Make sure to replace values with your own.

---

### Running with Docker Compose

This project uses Docker Compose to orchestrate multiple services.

Start the containers:

```bash
docker-compose up --build
```

This will launch:

- FastAPI app accessible at \`http://localhost:8000\`
- Celery worker processing background tasks
- PostgreSQL database on port \`5432\`
- Redis server on port \`6379\`

### Accessing the API

Open your browser or API client (e.g. Postman) and navigate to:

\`http://localhost:8000/docs\`

This will open the automatically generated OpenAPI interactive documentation.

---

### Running Services Individually

If you want to build and run the FastAPI app container individually:

```bash
docker build -t fastapi_app .
docker run -p 8000:8000 --env-file .env fastapi_app
```

To run the Celery worker separately:

```bash
docker run --env-file .env fastapi_app celery -A app.core.celery_worker.celery_app worker --pool=solo --loglevel=info
```

---

## Project Structure

- \`app/\` — FastAPI application source code
- \`app/api/routers/\` — FastAPI routers
- \`app/core/\` — Core logic, including Celery worker and auth
- \`app/db/\` — Database models and session management
- \`app/repositories/\` — Database repository classes
- \`app/schemas/\` — Pydantic schemas for data validation
- \`app/services/\` — Business logic and service layer
- \`app/tasks/\` — Celery tasks
- \`Dockerfile\` — Docker image configuration for FastAPI app
- \`docker-compose.yml\` — Docker Compose setup for multi-container environment

---

## Notes

- Celery uses Redis as a message broker and backend.
- PostgreSQL data is persisted in a Docker volume (\`pg_data\`).
- The FastAPI app is set to reload automatically during development (\`--reload\` flag).
- Adjust \`.env\` variables according to your environment and secrets.

---

## License

[MIT License](LICENSE)

---

## Contact

Created by Dmytro Tkach — feel free to reach out!
