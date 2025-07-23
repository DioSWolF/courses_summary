from pydantic import BaseModel
from typing import Optional


class CeleryTaskBase(BaseModel):
    task_id: str
    status: str
    course_id: int
    user_id: int
    result: Optional[str]


class CeleryTaskCreate(CeleryTaskBase):
    pass


class CeleryTaskRead(CeleryTaskBase):
    id: int

    class Config:
        from_attributes = True
