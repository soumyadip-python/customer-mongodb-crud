# Deploying customer-mongodb-crud to AWS EKS

This document explains how to build the Docker image for this FastAPI app, push it to a container registry (ECR), and deploy it to an EKS cluster. It also describes how to configure MongoDB Atlas connectivity.

Prerequisites
- AWS CLI configured with credentials
- kubectl configured to talk to your EKS cluster
- Docker installed and able to push to ECR

1) Build and push image to ECR

Replace the placeholders with your AWS account and region.

```powershell
# create an ECR repo (one-time)
aws ecr create-repository --repository-name customer-api --region <region>

# login
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

# build
docker build -t customer-api .

# tag and push
docker tag customer-api:latest <account>.dkr.ecr.<region>.amazonaws.com/customer-api:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/customer-api:latest
```

2) Create Kubernetes Secret for MongoDB credentials

Use the example `k8s/secret-example.yaml` as a template or create from CLI:

```powershell
kubectl create secret generic mongo-creds \
  --from-literal=DB_USER='your-db-user' \
  --from-literal=DB_PASSWORD='your-db-password' \
  --from-literal=DB_CLUSTER='ac-yourcluster.mongodb.net' \
  --from-literal=DB_NAME='your-db-name'
```

3) Update and apply Deployment

- Edit `k8s/deployment.yaml`, replace `<REPLACE_WITH_YOUR_REGISTRY>` with your ECR image path.
- Apply manifests:

```powershell
kubectl apply -f k8s/secret-example.yaml   # if using the YAML example (optional)
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

4) Accessing the app

- For development you can port-forward the service:

```powershell
kubectl port-forward svc/customer-api 8080:80
# then open http://localhost:8080/docs
```

5) Networking notes
- If you use Atlas public endpoints, ensure your cluster nodes (or NAT gateway) IP is allowlisted in Atlas Network Access.
- For production, use Atlas PrivateLink or VPC Peering.

6) Troubleshooting
- If Atlas still fails with TLS errors from the pod, check outbound egress (NAT, security groups, NACLs) and DNS resolution from within a pod.
  - Run an ephemeral debug pod: `kubectl run -it --rm --image=python:3.11 debug -- bash`
  - Inside the pod run: `python -c "import socket,ssl; s=socket.create_connection(('ac-...mongodb.net',27017),10); ctx=ssl.create_default_context(); ss=ctx.wrap_socket(s,server_hostname='ac-...mongodb.net'); print(ss.version()); ss.close()"`
