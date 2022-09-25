import logging
import os
import boto3
import json
import models

logger = logging.getLogger(__name__)

endpoint_url = os.getenv("AWS_ENDPOINT_URL")
sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
job_queue = sqs.get_queue_by_name(QueueName='job-queue')
job_result_queue = sqs.get_queue_by_name(QueueName='job-result-queue')


def send_job_message(job: models.Job):
    job_queue.send_message(
        MessageBody=json.dumps({
            'id': job.id,
            'timeSeconds': job.timeSeconds
        })
    )


def consume_job_result_messages():
    logger.info("Getting job results")
    return job_result_queue.receive_messages(MaxNumberOfMessages=10)
    