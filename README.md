# data-analytics-app-architecture-aws

Monorepo that represents a full architectural solution for a simple data analytics app

# structure

documentation repository describes high level architecture
iac repository 

# how to use

1. Read the documentation repository first.
2. Set up AWS account and create user with programmatic access and admin access to your AWS account. We will use its credentials in github actions to set up the environment.
3. In github go to the repository -> settings -> secrets -> actions and add the following parameters

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_ACCOUNT_ID
    AWS_DEFAULT_REGION

4. Launch `aws_init` github action. It will create s3 bucket for terraform and two ECR repositories for `api` and `worker`. 

NOTE: If you have created your AWS account recently you need to launch an EC2 instance to remove account limitations [give reference]. You can stop it once you receive an email from AWS about acount activation.

5. Launch `api_build` github action