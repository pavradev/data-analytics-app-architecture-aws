import enum
from sqlalchemy import Enum, Column, Integer
from .database import Base
from .schemas import JobStatus

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    timeSeconds = Column(Integer, nullable=False)
    status = Column(Enum(JobStatus), nullable=False)
    completedInSec: int