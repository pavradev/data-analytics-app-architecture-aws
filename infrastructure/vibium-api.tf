#
# Load balancer
#
resource "aws_security_group" "api_lb" {
  name        = "security-group-api-lb"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "api" {
  name            = "lb-api"
  subnets         = data.aws_subnets.all.ids
  security_groups = [aws_security_group.api_lb.id]
}

resource "aws_lb_target_group" "api_ecs" {
  name        = "target-group-ecs"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"
}

resource "aws_lb_listener" "api_80" {
  load_balancer_arn = aws_lb.api.id
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_lb_target_group.api_ecs.id
    type             = "forward"
  }
}

#
# ECS Fargate cluster
#
resource "aws_ecs_cluster" "api" {
  name = "ecs-cluster-api"
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/ecs/api-logs"
  retention_in_days = 14
}

resource "aws_iam_role" "api_task_execution_role" {
  name = "ApiTaskExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.ecs_assume_role_policy.json}"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]
}

resource "aws_iam_role" "api_task_role" {
  name = "ApiTaskRole"
  assume_role_policy = "${data.aws_iam_policy_document.ecs_assume_role_policy.json}"
}

resource "aws_iam_role_policy_attachment" "api_job_queue_write" {
  role       = "${aws_iam_role.api_task_role.name}"
  policy_arn = "${aws_iam_policy.job_queue_write.arn}"
}

resource "aws_security_group" "api_task" {
  name        = "security-group-api-task"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol        = "tcp"
    from_port       = 8000
    to_port         = 8000
    security_groups = [aws_security_group.api_lb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "api-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  task_role_arn = resource.aws_iam_role.api_task_role.arn
  execution_role_arn = resource.aws_iam_role.api_task_execution_role.arn
  container_definitions = <<DEFINITION
[
  {
    "image": "${data.aws_caller_identity.current.account_id}.dkr.ecr.eu-west-1.amazonaws.com/api:latest",
    "cpu": 512,
    "memory": 1024,
    "name": "app",
    "networkMode": "awsvpc",
    "portMappings": [
      {
        "containerPort": 8000,
        "hostPort": 8000
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/aws/ecs/api-logs",
        "awslogs-region": "${data.aws_region.current.name}",
        "awslogs-stream-prefix": "container"
      }
    },
    "environment": [
    ]
  }
]
DEFINITION
}

resource "aws_ecs_service" "api" {
  name            = "service-api"
  cluster         = aws_ecs_cluster.api.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups     = [aws_security_group.api_task.id]
    subnets             = data.aws_subnets.all.ids
    assign_public_ip    = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api_ecs.id
    container_name   = "app"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.api_80]
}

output "api_url" {
  value = aws_lb.api.dns_name
}