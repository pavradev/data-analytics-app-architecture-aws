#!/usr/bin/env bash
set -x
awslocal sqs create-queue --region eu-west-1 --queue-name job-queue
set +x
