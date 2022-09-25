import os
import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from time import sleep
from typing import List
from fastapi import FastAPI, Depends
import boto3
import logging
import json
from sqlalchemy.orm import Session
import repository, database, schemas


# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
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


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)  # wait and return result


def consume_messages():
    try:
        db = database.SessionLocal()
        logger.info("Getting job results")
        for message in job_result_queue.receive_messages(MaxNumberOfMessages=10):
            logging.info("Received job result %s ", message.body)
            body = json.loads(message.body)
            repository.update_job_status(db=db, id=body.get('id'), status=schemas.JobStatus.COMPLETED)
            message.delete()
    finally:
        db.close()


async def listen_to_job_results():
    logger.info("Starting job result listener")
    while True:
        await asyncio.sleep(5)
        await run_in_process(consume_messages)


@app.on_event('startup')
async def startup():
    app.state.executor = ProcessPoolExecutor()
    asyncio.create_task(listen_to_job_results())


@app.on_event('shutdown')
async def stop():
    app.state.executor.shutdown()


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