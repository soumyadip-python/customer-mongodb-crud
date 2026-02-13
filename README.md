# customer-mongodb-crud — deploy to AWS (CodeBuild → ECR → ECS Fargate)

This repository contains a small FastAPI service that reads/writes customer data to MongoDB Atlas. The project includes a Dockerfile and artifacts to build and deploy the service to AWS using CodeBuild (build & push image to ECR) and ECS Fargate (run container).

This README documents a Console-focused CodeBuild → ECR → ECS workflow. It assumes you have an AWS account and the necessary console permissions.

Overview (high level)
- Create an ECR repo to host the Docker image.
- Store MongoDB credentials in AWS Secrets Manager.
- Create a CodeBuild project that builds the Docker image and pushes to ECR (uses `buildspec.yml` in repo root).
- Create an ECS Fargate cluster and a Service that runs the Task Definition (`ecs/task-def.json`) referencing Secrets Manager values.
- Expose the service with an Application Load Balancer (ALB) and test.

Safety first
- Do NOT commit secrets. This repo ignores virtualenv and `.env` by default. If you accidentally committed credentials, rotate them and remove from history.
- For production, use Atlas PrivateLink or VPC peering and keep your cluster in private subnets.

Files you will use
- `Dockerfile` — builds the FastAPI app image.
- `buildspec.yml` — CodeBuild instructions to build & push the image to ECR.
- `ecs/task-def.json` — example Fargate task definition (replace placeholders).
- `ecs/deploy-to-ecs.sh` — helper script to register task definition and update ECS service (for Cloud9 or local AWS CLI).

1) Create an ECR repository

Console steps:
- Open AWS Console → ECR → Repositories → Create repository.
- Name: `customer-api` (or your preferred name). Keep defaults.

Note the repository URI (e.g. <account>.dkr.ecr.<region>.amazonaws.com/customer-api) — you'll use this in CodeBuild.

2) Store MongoDB credentials in Secrets Manager

Console steps:
- AWS Console → Secrets Manager → Store a new secret → Other type of secret (key/value)
- Add keys:
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_CLUSTER` (e.g. ac-xxxx.mongodb.net)
  - `DB_NAME`
- Secret name: `customer-api/mongo` (used in `ecs/task-def.json` examples)

3) Create a CodeBuild project (build & push image)

We use the included `buildspec.yml`. It expects an environment variable `REPOSITORY_URI` pointing to the ECR repo.

Console steps:
- AWS Console → CodeBuild → Create project
  - Source provider: GitHub (connect your GitHub account and select this repository and branch)
  - Environment: Managed image, Amazon Linux 2, Standard image that supports Docker (choose one that supports Docker)
    - Check “Privileged” to allow Docker builds
  - Service role: create a new service role (console wizard)
  - Environment variables: Add `REPOSITORY_URI` with value equal to your ECR repo URI (the buildspec uses it). Also set `AWS_DEFAULT_REGION` if desired.
  - Buildspec: Use the buildspec.yml in the repo (default)
  - Artifacts: No artifacts required

- Start a build. Watch the build logs in the CodeBuild console. If successful, the image will be pushed to ECR with tag `latest`.

4) Create an ECS cluster (Fargate) and register task definition

Console steps to create Cluster:
- ECS → Clusters → Create cluster → Networking only (for Fargate) → Create

Task Definition (register):
- ECS → Task Definitions → Create new Task Definition → FARGATE
  - Family: `customer-api-task` (or match `ecs/task-def.json`)
  - Task role / execution role: create or use `ecsTaskExecutionRole` (console can create it)
  - CPU/Memory: choose appropriate values (e.g. 512 / 1024)
  - Container definitions:
    - Image: paste the ECR image URI you pushed (e.g. <account>.dkr.ecr.<region>.amazonaws.com/customer-api:latest)
    - Port mappings: container port 8000
    - Log configuration: awslogs, group `/ecs/customer-api`
    - Environment/Secrets: configure secrets by choosing Secrets Manager and selecting your `customer-api/mongo` entries for DB_USER, DB_PASSWORD, DB_CLUSTER, DB_NAME

Or register the provided `ecs/task-def.json` (edit placeholders first) from the Console or CLI.

5) Create an Application Load Balancer and ECS Service

Console steps (high level):
- EC2 → Load Balancers → Create Load Balancer → Application Load Balancer
  - Scheme: internet-facing (for public access) or internal (private)
  - Listeners: HTTP 80 (or HTTPS if you configure cert)
  - Subnets: choose public subnets for ALB
  - Security group: allow inbound 80 from the internet (or restrict as needed)

- Target group: create a target group (Target type: IP) that listens on port 8000.

- ECS → Clusters → choose your cluster → Create → Create Service
  - Launch type: FARGATE
  - Task definition: choose your registered task
  - Service name: `customer-api-service`
  - Number of tasks: 1 or 2
  - Networking: choose VPC & private subnets for tasks (tasks should be in private subnets with NAT for internet egress) and a security group that allows outbound to Atlas
  - Load balancer: attach the ALB target group; container name/port should be `customer-api` / 8000

ECS will create tasks and register them with the target group. The ALB will route traffic to your tasks.

6) Confirm networking and Atlas access

- If you use Atlas public endpoints: ensure the NAT gateway IP (if tasks run in private subnets) or your task egress IP is added to Atlas Network Access (or use 0.0.0.0/0 temporarily for testing).
- For production: configure Atlas PrivateLink or VPC peering and adjust route tables/security groups accordingly.

7) Test the running service

- Get the ALB DNS name from the EC2 → Load Balancers console.
- Test the docs endpoint:

```powershell
curl http://<ALB_DNS>/docs
```

- Test API using curl/postman to POST/GET on `/customer` routes.

8) Helpful debugging

- Logs: CloudWatch Logs → `/ecs/customer-api`
- ECS Exec: enable SSM permissions on the task role and use `aws ecs execute-command` (or use Cloud9 to exec inside a task)

9) Alternative: Cloud9 or CodeBuild-only build

- If you prefer not to configure CodeBuild, Cloud9 is an easy browser-based dev environment with Docker and the AWS CLI installed. Clone the repo into Cloud9 and run the push steps from there (the README-EKS.md contains the Docker build commands if you want that route).

10) Clean up

- If you create temporary allowlist entries in Atlas (0.0.0.0/0) remove them after testing.
- Delete unused resources (ALB, ECR images, CodeBuild) to avoid charges.

Questions or next steps
- I can: add a GitHub Actions workflow that builds the image and triggers CodeBuild/ECS updates; or
- Walk through the Console screens with you step-by-step (I’ll provide exact clicks and fields). 

If you want the GitHub Actions workflow or the Cloud9 command list, tell me which and I’ll add it to the repo.
