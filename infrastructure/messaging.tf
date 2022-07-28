resource "aws_sqs_queue" "job_queue" {
  name = "job-queue"
  visibility_timeout_seconds = 600
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.job_queue_dlq.arn
    maxReceiveCount     = 3
  })
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.job_queue_dlq.arn]
  })
}

resource "aws_sqs_queue" "job_queue_dlq" {
  name = "job-queue-dlq"
}

data "aws_iam_policy_document" "job_queue_write" {
  statement {
    sid = ""
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:SendMessage",
      "sqs:GetQueueUrl",
      "sqs:DeleteMessage"
    ]
    resources = [
      aws_sqs_queue.job_queue.arn
    ]
  }
}

resource "aws_iam_policy" "job_queue_write" {
  name   = "data-sqs-writer-policy"
  policy = "${data.aws_iam_policy_document.job_queue_write.json}"
}