resource "aws_ecs_cluster" "worker" {
  name = "ecs-cluster-worker"
}

resource "aws_cloudwatch_log_group" "worker_logs" {
  name              = "/aws/ecs/worker-logs"
  retention_in_days = 14
}

resource "aws_iam_role" "worker_task_execution_role" {
  name = "WorkerTaskExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.ecs_assume_role_policy.json}"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]
}

resource "aws_iam_role" "worker_task_role" {
  name = "WorkerTaskRole"
  assume_role_policy = "${data.aws_iam_policy_document.ecs_assume_role_policy.json}"
}

resource "aws_iam_role_policy_attachment" "worker_in_queue_write" {
  role       = "${aws_iam_role.worker_task_role.name}"
  policy_arn = "${aws_iam_policy.job_queue_write.arn}"
}

resource "aws_security_group" "worker_task" {
  name        = "security-group-worker-task"
  vpc_id      = data.aws_vpc.default.id

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_task_definition" "worker" {
  family = "task-worker-app"
  container_definitions = jsonencode([
    {
      name      = "worker-app"
      image     = "${data.aws_caller_identity.current.account_id}.dkr.ecr.eu-west-1.amazonaws.com/worker:latest"
      cpu       = 0
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options   = {
          awslogs-group         = aws_cloudwatch_log_group.worker_logs.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix =  "container"
        }
      }
      environment = [
      ]
    }
  ])
  cpu = 512
  memory = 1024
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  task_role_arn = resource.aws_iam_role.worker_task_role.arn
  execution_role_arn = resource.aws_iam_role.worker_task_execution_role.arn
}