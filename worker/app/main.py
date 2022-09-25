import os
from time import sleep
import sys
import json
import logging
import boto3

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
endpoint_url = os.getenv("AWS_ENDPOINT_URL")

sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
job_queue = sqs.get_queue_by_name(QueueName='job-queue')
job_result_queue = sqs.get_queue_by_name(QueueName='job-result-queue')

def main():
    while 1:
        logging.info("Waiting for messages...")
        messages = job_queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=5)

        if(len(messages) == 0):
            logging.info("No messages in the queue. Shutting down...")
            return

        for message in messages:
            logging.info("Received job %s ", message.body)
            body = json.loads(message.body)
            executin_time = body.get('timeSeconds')
            logging.info("Sleeping %s seconds", executin_time)
            sleep(executin_time)
            job_result_queue.send_message(
                MessageBody=json.dumps({
                    'id': body.get('id'),
                    'executionTime': executin_time
                })
            )
            message.delete()

if __name__ == '__main__':
    main()