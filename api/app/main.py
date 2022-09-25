import os
import asyncio
from typing import List
from fastapi import FastAPI, Depends
import boto3
import logging
import json
from sqlalchemy.orm import Session
from app import repository, models, database, schemas

logger = logging.getLogger(__name__)

endpoint_url = os.getenv("AWS_ENDPOINT_URL")
sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
job_queue = sqs.get_queue_by_name(QueueName='job-queue')
job_result_queue = sqs.get_queue_by_name(QueueName='job-result-queue')

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def listen_to_job_results():
    logger.info("Starting job result listener")
    while True:
        try:
            await asyncio.sleep(5)
            db = database.SessionLocal()
            for message in job_result_queue.receive_messages(MaxNumberOfMessages=10):
                logging.info("Received job result %s ", message.body)
                body = json.loads(message.body)
                repository.update_job_status(db=db, id=body.get('id'), status=models.JobStatus.COMPLETED)
                message.delete()
        finally:
            db.close()


@app.on_event('startup')
async def startup():
    asyncio.create_task(listen_to_job_results())


@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job: schemas.JobIn, db: Session = Depends(get_db)):
    logger.info("Received job %s ", job)
    db_job = repository.create_job(db=db, item=job)
    job_queue.send_message(
        MessageBody=json.dumps({
            'id': db_job.id,
            'timeSeconds': db_job.timeSeconds
        })
    )
    return db_job


@app.get("/jobs", response_model=List[schemas.JobOut])
def create_job(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = repository.get_jobs(db=db, skip=skip, limit=limit)
    return jobs


# For debugging only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)