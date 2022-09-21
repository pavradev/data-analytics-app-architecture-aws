from typing import Optional
from pydantic import BaseModel
from enum import Enum

class JobStatus(Enum):
    CREATED = 1
    QUEUED = 2
    COMPLETED = 3
    ERROR = 4

class JobIn(BaseModel):
    timeSeconds: int

class JobOut(BaseModel):
    id: int
    timeSeconds: int
    status: JobStatus
    completedInSeconds: Optional[int]

    class Config:
        orm_mode = True
