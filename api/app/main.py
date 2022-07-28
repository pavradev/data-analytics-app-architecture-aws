import os
from fastapi import FastAPI, Response
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
import logging
import json

logger = logging.getLogger(__name__)
endpoint_url = os.getenv("AWS_ENDPOINT_URL")

sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
queue = sqs.get_queue_by_name(QueueName='job-queue')

class JobIn(BaseModel):
    timeSeconds: int

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/jobs")
def create_job(job: JobIn, response: Response):
    logger.info("Received job %s ", job)
    try:
        response = queue.send_message(
            MessageBody=json.dumps({'jobExectutionTime': job.timeSeconds})
        )
    except ClientError as error:
        logger.exception("Send message failed: %s", job)
        raise error
    else:
        logger.info("Message with id %s sent", response.get('MessageId'))
