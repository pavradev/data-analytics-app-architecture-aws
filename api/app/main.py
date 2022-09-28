from typing import List
from fastapi import FastAPI, Depends
import logging
import json
from sqlalchemy.orm import Session
from fastapi_utils.tasks import repeat_every
from . import repository, database, schemas, messaging, models, config, auth

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(thread)d - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

settings = config.get_settings()

# initialize db
database.Base.metadata.create_all(bind=database.engine)


def init_db():
    db = database.SessionLocal()
    try:
        admin = repository.find_user_by_key_id(db=db, key_id=settings.admin_key_id)
        if not admin:
            repository.create_user(db=db, user=models.User(
                name="admin", 
                role=models.Role.VIBIUM_ADMIN, 
                key_id=settings.admin_key_id,
                hashed_secret_key=settings.admin_hashed_secret_key))
    finally:
        db.close()


init_db()

# initialize app
app = FastAPI()

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
                repository.update_job_status(db=db, job_id=body.get('id'), status=models.JobStatus.COMPLETED)
                message.delete()
        finally:
            db.close()


@app.post("/admin/users", response_model=schemas.UserOut)
@auth.auth_check(roles = [models.Role.VIBIUM_ADMIN])
def create_job(user_in: schemas.UserIn, db: Session = Depends(database.get_db), user: models.User = Depends(auth.check_authentication_header)):
    [random_key_id, random_secret_key, hashed_secret_key] = auth.generate_random_key()
    db_user = models.User(**user_in.dict(), key_id=random_key_id, hashed_secret_key=hashed_secret_key)
    user_out = repository.create_user(db=db, user=db_user)
    user_out.secret_key = random_secret_key
    return user_out


@app.post("/jobs", response_model=schemas.JobOut)
@auth.auth_check(roles = [models.Role.CLIENT])
def create_job(job: schemas.JobIn, db: Session = Depends(database.get_db), user: models.User = Depends(auth.check_authentication_header)):
    logger.info("Received job %s for user %s", job, user.client_id)
    db_job = repository.create_client_job(db=db, client_id=user.client_id, item=job)
    messaging.send_job_message(job=db_job)
    return db_job


@app.get("/jobs", response_model=List[schemas.JobOut])
@auth.auth_check(roles = [models.Role.CLIENT])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), user: models.User = Depends(auth.check_authentication_header)):
    logger.info("Return all jobs for client %s", user.client_id)
    jobs = repository.get_client_jobs(db=db, client_id=user.client_id, skip=skip, limit=limit)
    return jobs


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)