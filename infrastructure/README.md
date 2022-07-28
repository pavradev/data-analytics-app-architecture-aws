# iac
Infrastructure as code repository for the project. Please note that the state is stored in AWS s3 bucket.

# prerequisites

- `Init AWS environment` github action that creates ECR repositories and s3 bucket for terraform state.
- api service docker image must exist in ECR repository
- worker service docker image must exist in ECR repository
- orchestrator docker image must exist in ECR repository
