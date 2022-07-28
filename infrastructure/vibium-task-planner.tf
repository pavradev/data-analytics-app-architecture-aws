resource "aws_iam_role" "lambda_orchestrator_role" {
  name = "OrchestratorRole"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_assume_role_policy.json}"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AmazonSQSReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
  ]
}

resource "aws_cloudwatch_event_rule" "orchestrator_schedule" {
  name = "orchestrator-schedule"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "orchestrator_target" {
  arn  = aws_lambda_function.orchestrator.arn
  rule = aws_cloudwatch_event_rule.orchestrator_schedule.id
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_orchestrator" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.orchestrator.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.orchestrator_schedule.arn
}

resource "aws_lambda_function" "orchestrator" {
  function_name = "orchestrator"
  role          = aws_iam_role.lambda_orchestrator_role.arn
  package_type  = "Image"
  image_uri     = "${data.aws_caller_identity.current.account_id}.dkr.ecr.eu-west-1.amazonaws.com/orchestrator:latest"

  environment {
    variables = {
      AWS_ECS_CLUSTER = aws_ecs_cluster.worker.name
      AWS_ECS_TASK_FAMILY = aws_ecs_task_definition.worker.family
      AWS_ECS_TASK_SECURITY_GROUPS = aws_security_group.worker_task.id
      AWS_ECS_TASK_SUBNETS = join(",", data.aws_subnets.all.ids)
    }
  }
}