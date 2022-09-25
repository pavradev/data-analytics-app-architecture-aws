from sqlalchemy import Enum, Column, Integer
import schemas, database

class Job(database.Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    timeSeconds = Column(Integer, nullable=False)
    status = Column(Enum(schemas.JobStatus), nullable=False)
    completedInSec: int