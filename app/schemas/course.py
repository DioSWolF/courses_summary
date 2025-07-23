from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CourseBase(BaseModel):
    course_title: str
    course_description: str


class CourseCreate(CourseBase):
    user_id: int


class CourseRead(CourseBase):
    id: int
    ai_summary: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
