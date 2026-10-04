#!/usr/bin/env bash
# EC2 Deployment Script: Pulls latest image from AWS ECR and runs it.
# Usage: ./scripts/deploy_ec2.sh <AWS_ACCOUNT_ID> <AWS_REGION> <ECR_REPOSITORY_NAME>

set -e

AWS_ACCOUNT_ID=${1:-"$AWS_ACCOUNT_ID"}
AWS_REGION=${2:-"${AWS_REGION:-us-east-1}"}
ECR_REPO_NAME=${3:-"${ECR_REPO_NAME:-cloud-microservice}"}

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "ERROR: AWS_ACCOUNT_ID is required as argument 1 or environment variable."
    echo "Usage: $0 <AWS_ACCOUNT_ID> [AWS_REGION] [ECR_REPO_NAME]"
    exit 1
fi

IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest"
CONTAINER_NAME="aws_cloud_microservice"

echo "=========================================================="
echo " Starting deployment on EC2 instance"
echo " Image: $IMAGE_URI"
echo " Region: $AWS_REGION"
echo "=========================================================="

# Authenticate Docker to AWS ECR
echo "1. Logging into AWS ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Pull latest container image
echo "2. Pulling latest Docker image from ECR..."
docker pull "$IMAGE_URI"

# Stop and remove existing container if running
echo "3. Stopping old container (if exists)..."
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    docker stop "$CONTAINER_NAME"
fi
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    docker rm "$CONTAINER_NAME"
fi

# Run new container
echo "4. Running new microservice container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 80:8000 \
    -e APP_ENV=production \
    --restart unless-stopped \
    "$IMAGE_URI"

# Verify health check
echo "5. Verifying container health..."
sleep 5
for i in {1..6}; do
    if curl -s -f http://localhost/health > /dev/null; then
        echo "Deployment successful! Microservice is healthy on port 80."
        docker ps -f name="$CONTAINER_NAME"
        exit 0
    fi
    echo "Waiting for health check... ($i/6)"
    sleep 3
done

echo "WARNING: Health check timed out, please inspect container logs with: docker logs $CONTAINER_NAME"
exit 1
