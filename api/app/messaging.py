import logging
import boto3
import json
from . import models, config

settings = config.get_settings()
logger = logging.getLogger(__name__)

sqs = boto3.resource("sqs", endpoint_url=settings.aws_endpoint_url)
job_queue = sqs.get_queue_by_name(QueueName='job-queue')
job_result_queue = sqs.get_queue_by_name(QueueName='job-result-queue')


def send_job_message(job: models.Job):
    job_queue.send_message(
        MessageBody=json.dumps({
            'id': job.id,
            'timeSeconds': job.time_seconds
        })
    )


def consume_job_result_messages():
    logger.info("Getting job results")
    return job_result_queue.receive_messages(MaxNumberOfMessages=10)
    