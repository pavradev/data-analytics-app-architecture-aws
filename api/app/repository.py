from sqlalchemy.orm import Session
from app import models, schemas

def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Job).offset(skip).limit(limit).all()


def create_job(db: Session, item: schemas.JobIn):
    db_job = models.Job(**item.dict(), status=schemas.JobStatus.CREATED)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job_status(db: Session, id: int, status=schemas.JobStatus):
    db_job = db.query(models.Job).filter_by(id=id).one()
    db_job.status = status
    db.commit()
    db.refresh(db_job)
    return db_job

