#!/usr/bin/env bash
set -x
awslocal sqs create-queue --region eu-west-1 --queue-name job-queue
awslocal sqs create-queue --region eu-west-1 --queue-name job-result-queue
set +x
