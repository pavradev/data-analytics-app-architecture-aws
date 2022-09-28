from pydantic import BaseModel
from . import models

class JobIn(BaseModel):
    time_seconds: int

class JobOut(BaseModel):
    id: int
    time_seconds: int
    status: models.JobStatus

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    name: str
    role: models.Role
    client_id: str


class UserOut(BaseModel):
    id: int
    name: str
    role: models.Role
    client_id: str
    key_id: str
    secret_key: str

    class Config:
        orm_mode = True