from sqlalchemy.orm import Session
from cachetools import cached
from cachetools.keys import hashkey
from . import models, schemas

def get_client_jobs(db: Session, client_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Job).filter_by(client_id=client_id).offset(skip).limit(limit).all()


def create_client_job(db: Session, client_id: str, item: schemas.JobIn):
    db_job = models.Job(**item.dict(), client_id=client_id, status=models.JobStatus.CREATED)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job_status(db: Session, job_id: int, status=models.JobStatus):
    db_job = db.query(models.Job).filter_by(id=job_id).one()
    db_job.status = status
    db.commit()
    db.refresh(db_job)
    return db_job


def create_user(db: Session, user: models.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@cached(
    cache={},
    key=lambda db, key_id: hashkey(key_id)
)
def find_user_by_key_id(db: Session, key_id: str) -> models.User:
    return db.query(models.User).filter_by(key_id=key_id).first()

