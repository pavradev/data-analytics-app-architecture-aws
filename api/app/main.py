import os
from typing import List
from fastapi import FastAPI, Depends
import boto3
from botocore.exceptions import ClientError
import logging
import json
from sqlalchemy.orm import Session
from . import repository, models, schemas
from .database import SessionLocal, engine

logger = logging.getLogger(__name__)
endpoint_url = os.getenv("AWS_ENDPOINT_URL")

sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
queue = sqs.get_queue_by_name(QueueName='job-queue')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job: schemas.JobIn, db: Session = Depends(get_db)):
    logger.info("Received job %s ", job)
    db_job = repository.create_job(db=db, item=job)
    queue.send_message(
        MessageBody=json.dumps({'jobExectutionTime': job.timeSeconds})
    )
    return db_job


@app.get("/jobs", response_model=List[schemas.JobOut])
def create_job(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = repository.get_jobs(db=db, skip=skip, limit=limit)
    return jobs