from sqlalchemy import Enum, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
import enum
from . import database

class JobStatus(enum.Enum):
    CREATED = 'CREATED'
    QUEUED = 'QUEUED'
    COMPLETED = 'COMPLETED'
    ERROR = 'ERROR'

class Role(enum.Enum):
    CLIENT = 'CLIENT'
    VIBIUM_ADMIN = 'VIBIUM_ADMIN'

class ClientRefMixin():
    @declared_attr
    def client_id(csl):
        return Column(String, nullable=False)


class User(database.Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(Role), nullable=False)
    client_id = Column(String)
    name = Column(String, nullable=False)
    key_id = Column(String, nullable=False, unique=True)
    hashed_secret_key = Column(String)


class Job(ClientRefMixin, database.Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    time_seconds = Column(Integer, nullable=False)
    status = Column(Enum(JobStatus), nullable=False)