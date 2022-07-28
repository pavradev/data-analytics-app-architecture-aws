import os
import boto3

sqs = boto3.resource('sqs')
ecs = boto3.client('ecs')

job_queue = os.getenv('AWS_JOB_QUEUE', 'job-queue')
ecs_cluster = os.getenv('AWS_ECS_CLUSTER')
ecs_task_family = os.getenv('AWS_ECS_TASK_FAMILY')
ecs_task_security_groups= os.getenv('AWS_ECS_TASK_SECURITY_GROUPS').split(',')
ecs_task_subnets= os.getenv('AWS_ECS_TASK_SUBNETS').split(',')

max_queue_size_per_task = int(os.getenv('MAX_QUEUE_SIZE_PER_TASK', 4))
max_parallel_tasks = int(os.getenv('MAX_PARALLEL_TASKS', 10))

def handler(event=None, context=None):
    queue = sqs.get_queue_by_name(QueueName=job_queue)
    message_count = int(queue.attributes['ApproximateNumberOfMessages'])
    print(f'Approximate {message_count} number of messages in queue')
    task_list = ecs.list_tasks(
        cluster=ecs_cluster,
        family=ecs_task_family,
        maxResults=max_parallel_tasks,
        desiredStatus='RUNNING',
    )
    task_count = len(task_list['taskArns'])
    print(f'Current number of tasks: {task_count}')
    expected_task_count = max(min(1, message_count), int(round(message_count / max_queue_size_per_task)))
    print(f'Expected number of tasks: {expected_task_count}')
    tasks_to_start = min(max_parallel_tasks - task_count, expected_task_count - task_count)
    if tasks_to_start > 0 :
        print(f'Will start {tasks_to_start} new tasks')
        resp = ecs.run_task(
            taskDefinition=ecs_task_family,
            cluster=ecs_cluster,
            count=tasks_to_start,
            launchType='FARGATE',
            networkConfiguration= {
                'awsvpcConfiguration': {
                    'subnets': ecs_task_subnets,
                    'securityGroups': ecs_task_security_groups,
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        print(resp)
    else:
        print('No new workers will be started')


if __name__ == '__main__':
    handler({}, {})