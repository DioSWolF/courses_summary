from fastapi import FastAPI
from app.api.routers import users, courses, summary, celery_tasks
from app.db import session
from app.db.base import Base


app = FastAPI()


@app.on_event("startup")
async def startup():
    async with session.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(summary.router, prefix="/generate_summary", tags=["Summary"])
app.include_router(celery_tasks.router, prefix="/celery_tasks", tags=["Celery tasks"])
