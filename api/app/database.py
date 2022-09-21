import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

pg_password = os.getenv("POSTGRES_PASSWORD")
pg_server = os.getenv("POSTGRES_SERVER")
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:" + pg_password + "@" + pg_server + "/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
