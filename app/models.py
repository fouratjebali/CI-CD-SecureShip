from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    done: bool = False

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""