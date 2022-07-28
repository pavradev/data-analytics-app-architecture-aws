# data-analytics-app-architecture-aws

Monorepo that represents a full architectural solution for a simple data analytics app

# structure

![documentation](./documentation/architecture.md) repository describes high level architecture
![iac](./iac/README.md) repository contains terraform configuration that deploys AWS infrastructure components
![api](./api/README.md) repository contains api service code

# running locally

You need docker with docker-compose to run locally. We will use ![localstack]() to AWS job-queue locally. Also note that `orchestrator` is not started when running locally. Insteat, docker-compose will make sure that 1 instance of `woker` is always running.

# running on AWS

1. Set up AWS account and create user with programmatic access and admin access to your AWS account. We will use its credentials in github actions to set up the environment.
2. Fork this github repository to your account. Go to the repository -> settings -> secrets -> actions and add the following parameters from your AWS account:

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_ACCOUNT_ID
    AWS_DEFAULT_REGION

3. Launch `aws_init` github action. It will create s3 bucket for terraform and tree ECR repositories for `api`, `worker`, and `orchestrator`. 

NOTE: If you have created your AWS account recently you need to launch an EC2 instance to remove account limitations [give reference]. You can stop it once you receive an email from AWS about acount activation.

4. Launch `api_build` github action