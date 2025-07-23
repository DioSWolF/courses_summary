from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, JSON
from app.db.base import Base


class CeleryTask(Base):
    __tablename__ = "celery_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    status = Column(String(20), nullable=False)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
