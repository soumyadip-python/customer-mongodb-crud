#!/bin/bash
# Simple helper script to register the task definition and update the ECS service.
# Fill in the placeholders below before running, or export them as environment variables.

set -euo pipefail

ACCOUNT=${ACCOUNT:-"<ACCOUNT>"}
REGION=${REGION:-"<REGION>"}
CLUSTER=${CLUSTER:-"customer-api-cluster"}
SERVICE=${SERVICE:-"customer-api-service"}
TASK_FAMILY=${TASK_FAMILY:-"customer-api-task"}
IMAGE=${IMAGE:-"$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/customer-api:latest"}

echo "Registering task definition..."
TASK_DEF_ARN=$(aws ecs register-task-definition --cli-input-json file://ecs/task-def.json --region $REGION --query 'taskDefinition.taskDefinitionArn' --output text)
echo "Registered: $TASK_DEF_ARN"

echo "Updating service $SERVICE in cluster $CLUSTER to use $TASK_DEF_ARN"
aws ecs update-service --cluster $CLUSTER --service $SERVICE --task-definition $TASK_DEF_ARN --region $REGION

echo "Service update requested. Check ECS Console or 'aws ecs describe-services' for status." 

# Notes:
# - Ensure ecs/task-def.json has placeholders replaced (image, ARNs) or export TASK_ROLE/EXEC_ROLE ARNs.
# - You must have AWS CLI v2 configured with permissions to register task definitions and update services.
