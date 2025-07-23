from enum import Enum

from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class CourseStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    finalized = "finalized"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_title = Column(String(255), nullable=False)
    course_description = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)
    status = Column(String(50), default=CourseStatus.pending.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="courses")
