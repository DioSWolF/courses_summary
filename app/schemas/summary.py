from pydantic import BaseModel


class SummaryUpdate(BaseModel):
    summary: str
