from typing import List
from fastapi import FastAPI, Depends
import logging
import json
from sqlalchemy.orm import Session
import repository, database, schemas, messaging
from fastapi_utils.tasks import repeat_every

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(thread)d - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event('startup')
@repeat_every(seconds=5)
def startup():
    messages = messaging.consume_job_result_messages()
    if len(messages) > 0:
        try:
            db = database.SessionLocal()
            for message in messages:
                logging.info("Received job result %s ", message.body)
                body = json.loads(message.body)
                repository.update_job_status(db=db, id=body.get('id'), status=schemas.JobStatus.COMPLETED)
                message.delete()
        finally:
            db.close()


@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job: schemas.JobIn, db: Session = Depends(get_db)):
    logger.info("Received job %s ", job)
    db_job = repository.create_job(db=db, item=job)
    messaging.send_job_message(job=db_job)
    return db_job


@app.get("/jobs", response_model=List[schemas.JobOut])
def create_job(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info("Return all jobs")
    jobs = repository.get_jobs(db=db, skip=skip, limit=limit)
    return jobs


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)