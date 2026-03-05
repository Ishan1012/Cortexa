# Cortexa Deployment Guide

## Table of Contents

1. [Deployment Strategy Overview](#deployment-strategy-overview)
2. [Phase 1: Initial Deployment (Vercel & Render)](#phase-1-initial-deployment-vercel--render)
3. [Phase 2: Containerization (Docker)](#phase-2-containerization-docker)
4. [Phase 3: Production Deployment (AWS)](#phase-3-production-deployment-aws)
5. [Domain Configuration](#domain-configuration)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring & Logging](#monitoring--logging)
8. [Health Checks & Alerting](#health-checks--alerting)
9. [Disaster Recovery](#disaster-recovery)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting Guide](#troubleshooting-guide)

---

## Deployment Strategy Overview

Cortexa uses a **phased deployment approach** for maximum reliability and risk mitigation:

```
┌─────────────────────────────────────────────────────────────┐
│                   PHASE 1: STAGING                          │
│         (Vercel & Render - Development Testing)             │
│                                                             │
│  - Frontend: Vercel                                         │
│  - Backend APIs: Render                                     │
│  - Database: PostgreSQL on Render/Atlas                     │
│  - Duration: 2-4 weeks                                      │
│  - Goal: Validate architecture, load testing, security      │
└────────────────────┬────────────────────────────────────────┘
                     │ (after successful testing)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 2: CONTAINERIZATION                      │
│           (Docker Build & Optimization)                     │
│                                                             │
│  - Create Dockerfiles for all services                      │
│  - Test container builds locally                            │
│  - Push to container registry (ECR)                         │
│  - Verify multi-container orchestration                     │
│  - Duration: 1-2 weeks                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ (after Docker validation)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         PHASE 3: PRODUCTION (AWS & Domain)                  │
│          (Scalable, Secure, Enterprise-grade)               │
│                                                             │
│  - Frontend: CloudFront + S3                                │
│  - Express API: ECS + ALB                                   │
│  - FastAPI: ECS + ALB                                       │
│  - Database: RDS PostgreSQL (Multi-AZ)                      │
│  - Caching: ElastiCache Redis                               │
│  - Domain: Route53 + Custom Domain                          │
│  - SSL/TLS: AWS Certificate Manager                         │
│  - Duration: 2-3 weeks                                      │
│  - Goal: Production-ready, 99.9% uptime SLA                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Initial Deployment (Vercel & Render)

### Vercel Deployment (Frontend)

#### Prerequisites

```bash
# Install Vercel CLI
npm install -g vercel

# Authenticate with Vercel account
vercel login
```

#### Deployment Steps

**Step 1: Configure Vercel Project**

```bash
cd apps/web-app

# Initialize Vercel project
vercel

# This will prompt for:
# - Project name: cortexa-frontend
# - Framework: Next.js
# - Build command: npm run build
# - Output directory: .next
```

**Step 2: Environment Variables**

Create `.env.production` in `apps/web-app`:

```env
# API endpoints
NEXT_PUBLIC_API_URL=https://api-staging.render.com/api/v1
NEXT_PUBLIC_INFERENCE_API_URL=https://inference-staging.render.com/api/v1

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Feature flags
NEXT_PUBLIC_FEATURE_PDF_GENERATION=true
NEXT_PUBLIC_FEATURE_IMAGE_UPLOAD=true
```

**Step 3: Deploy to Vercel**

```bash
vercel --prod

# Output:
# ✓ Production deployment complete
# ✓ URL: https://cortexa-staging.vercel.app
```

**Step 4: Configure Vercel Settings**

In Vercel Dashboard:
- **Domains**: Add `staging-frontend.cortexa.local` (or custom domain)
- **Environment Variables**: Add from `.env.production`
- **Build Settings**: 
  - Build Command: `npm run build`
  - Output Directory: `.next`
- **Caching**: Enable automatic cache on production deployments
- **Analytics**: Enable Web Analytics
- **Monitoring**: Enable Vercel Analytics

#### Vercel Monitoring

```bash
# View deployment logs
vercel logs

# Monitor real-time metrics
# Dashboard: https://vercel.com/dashboard

# Check deployment status
vercel status
```

---

### Render Deployment (Backend APIs)

#### Prerequisites

- Create Render account (https://render.com)
- Link GitHub repository

#### Deploy Express Orchestrator

**Step 1: Create Render Service**

1. Go to Render Dashboard → New Service
2. Select "Web Service"
3. Connect GitHub repository
4. Configuration:

```yaml
Name: cortexa-express-api
Region: Oregon (us-west)  # Closest to Vercel
Runtime: Node
Build Command: npm install && npm run build
Start Command: npm run start
```

**Step 2: Environment Variables**

In Render Dashboard → Environment:

```env
NODE_ENV=production
PORT=3000
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@render-postgres:5432/cortexa_db
DATABASE_SSL=true

# Encryption
ENCRYPTION_KEY=[32-byte hex string from secure generation]
JWT_SECRET=[secure random string]
JWT_EXPIRY=1800

# External Services
FASTAPI_URL=https://inference-api-staging.render.com/api/v1
ENCRYPTION_SERVICE_URL=https://crypto-api-staging.render.com/api/v1

# AWS (for file uploads)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=[from IAM user]
AWS_SECRET_ACCESS_KEY=[from IAM user]
AWS_S3_BUCKET=cortexa-signals-staging

# Email (for reports)
SENDGRID_API_KEY=[from SendGrid]
SENDGRID_FROM_EMAIL=noreply@cortexa.staging
```

**Step 3: Deploy**

```bash
# Render auto-deploys on push to main branch
# Monitor in Render Dashboard: https://dashboard.render.com/
```

#### Deploy FastAPI Inference Engine

**Step 1: Create Render Service**

1. New Service → Web Service
2. Configuration:

```yaml
Name: cortexa-fastapi
Region: Oregon (us-west)
Runtime: Python 3.9
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 2: Environment Variables**

```env
ENVIRONMENT=production
LOG_LEVEL=info
WORKERS=4

# Model paths
MODEL_REGISTRY_PATH=/models
WEIGHT_S3_PATH=s3://cortexa-models-staging/

# Database
DATABASE_URL=postgresql://user:password@render-postgres:5432/cortexa_db

# Feature flags
ENABLE_IMAGE_PREPROCESSING=true
ENABLE_MULTI_CONDITION_PREDICTION=true
```

**Step 3: Deploy**

Render auto-deploys on GitHub push to main branch.

#### Set Up Database on Render

**Step 1: Create PostgreSQL Instance**

1. New Service → PostgreSQL
2. Configuration:

```yaml
Name: cortexa-postgres-staging
Database: cortexa_db
User: cortexa_user
Plan: Standard (for staging)
```

**Step 2: Initialize Database**

```bash
# Connect to Render PostgreSQL
PGPASSWORD=[password] psql -h [hostname] -U cortexa_user -d cortexa_db

# Run migrations
\i scripts/init_database.sql
\i scripts/seed_data.sql

# Verify tables
\dt
```

**Step 3: Backup Configuration**

```bash
# Enable automated backups in Render Dashboard
# In PostgreSQL service settings:
# - Backup frequency: Daily
# - Retention: 30 days
```

---

### Phase 1 Testing

#### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test Express API (100 requests, 10 concurrent)
ab -n 100 -c 10 https://api-staging.render.com/api/v1/health

# Test FastAPI (1000 requests, 50 concurrent)
ab -n 1000 -c 50 https://inference-staging.render.com/api/v1/health

# Using k6 for more complex load testing
k6 run scripts/load-test.js
```

#### Integration Testing

```bash
# Run full test suite against staging
npm run test:integration -- --baseUrl=https://api-staging.render.com

# Output: All 256 tests passed
```

#### Security Testing

```bash
# OWASP ZAP scan
zaproxy -cmd -quickurl https://staging-frontend.cortexa.local \
  -quickout zap-report.html

# Dependency vulnerability check
npm audit
pip audit
```

---

## Phase 2: Containerization (Docker)

### Express Orchestrator Dockerfile

**File: `infra/docker/express.Dockerfile`**

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY services/express-api/package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY services/express-api/src ./src
COPY services/express-api/tsconfig.json ./

# Build TypeScript
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1000 nodejs && \
    adduser -S nodejs -u 1000

# Copy dependencies from builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist

# Copy health check script
COPY --chown=nodejs:nodejs scripts/health-check.js ./

# Switch to non-root user
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD node health-check.js || exit 1

# Expose port
EXPOSE 3000

# Use dumb-init to handle signals
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "dist/server.js"]
```

### FastAPI Dockerfile

**File: `infra/docker/fastapi.Dockerfile`**

```dockerfile
# Build stage
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/fast-api/requirements.txt ./

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 fastapi

# Copy virtual environment
COPY --from=builder --chown=fastapi:fastapi /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=fastapi:fastapi services/fast-api/app ./app
COPY --chown=fastapi:fastapi services/fast-api/config.yaml ./

# Copy health check script
COPY --chown=fastapi:fastapi scripts/health-check-fastapi.py ./

# Switch to non-root user
USER fastapi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python health-check-fastapi.py || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose for Local Testing

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: cortexa-postgres
    environment:
      POSTGRES_DB: cortexa_db
      POSTGRES_USER: cortexa_user
      POSTGRES_PASSWORD: SecurePassword123!
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_database.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - cortexa-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cortexa_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: cortexa-redis
    ports:
      - "6379:6379"
    networks:
      - cortexa-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Express Orchestrator API
  express-api:
    build:
      context: .
      dockerfile: infra/docker/express.Dockerfile
    container_name: cortexa-express
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://cortexa_user:SecurePassword123!@postgres:5432/cortexa_db
      REDIS_URL: redis://redis:6379
      FASTAPI_URL: http://fastapi-api:8000/api/v1
      JWT_SECRET: your-super-secret-key-32-chars-minimum
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - cortexa-network
    restart: unless-stopped

  # FastAPI Inference Engine
  fastapi-api:
    build:
      context: .
      dockerfile: infra/docker/fastapi.Dockerfile
    container_name: cortexa-fastapi
    environment:
      ENVIRONMENT: production
      DATABASE_URL: postgresql://cortexa_user:SecurePassword123!@postgres:5432/cortexa_db
      LOG_LEVEL: info
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - cortexa-network
    restart: unless-stopped
    shm_size: '2gb'  # Shared memory for PyTorch

  # Next.js Frontend
  frontend:
    build:
      context: ./apps/web-app
      dockerfile: Dockerfile
    container_name: cortexa-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:3000/api/v1
      NEXT_PUBLIC_INFERENCE_URL: http://localhost:8000/api/v1
    ports:
      - "3001:3000"
    depends_on:
      - express-api
    networks:
      - cortexa-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  cortexa-network:
    driver: bridge
```

### Docker Build & Push

```bash
# Build images
docker build -f infra/docker/express.Dockerfile -t cortexa/express-api:1.0.0 .
docker build -f infra/docker/fastapi.Dockerfile -t cortexa/fastapi-api:1.0.0 .

# Tag for ECR
docker tag cortexa/express-api:1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/cortexa-express:latest
docker tag cortexa/fastapi-api:1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/cortexa-fastapi:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/cortexa-express:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/cortexa-fastapi:latest
```

### Test Docker Containers Locally

```bash
# Start all containers
docker-compose up --build

# Check container health
docker ps

# View logs
docker-compose logs -f express-api
docker-compose logs -f fastapi-api

# Run integration tests
docker-compose exec express-api npm run test:integration

# Stop containers
docker-compose down
```

---

## Phase 3: Production Deployment (AWS)

### AWS Architecture

```
┌─────────────────────────────────────────────┐
│          Route53 (DNS)                      │
│      api.cortexa.clinical /                 │
│      app.cortexa.clinical                   │
└────────────┬────────────────────────────────┘
             │
        ┌────┴───────┐
        │            │
        ▼            ▼
  ┌─────────────┐  ┌──────────┐
  │ CloudFront  │  │ ALB      │
  │ (Frontend)  │  │ (APIs)   │
  └──────┬──────┘  └──┬───────┘
         │            │
    ┌────▼────┐   ┌──┴──────┬──────────┐
    │    S3   │   │   ECS   │ ECS      │
    │ (Files) │   │(Express)│(FastAPI) │
    └─────────┘   └─────────┴──────────┘
                        │
                   ┌────▼───────┐
                   │ RDS (DB)   │
                   └────────────┘
```

### Prerequisites

```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter:
# AWS Access Key ID: [from IAM user]
# AWS Secret Access Key: [from IAM user]
# Default region: us-east-1
# Default output format: json

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.3.0/terraform_1.3.0_linux_amd64.zip
unzip terraform_1.3.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### Create ECR Registry

```bash
# Create repository for Express API
aws ecr create-repository \
  --repository-name cortexa-express \
  --region us-east-1 \
  --encryption-configuration encryptionType=AES

# Create repository for FastAPI
aws ecr create-repository \
  --repository-name cortexa-fastapi \
  --region us-east-1 \
  --encryption-configuration encryptionType=AES

# Set image scanning
aws ecr put-image-scanning-configuration \
  --repository-name cortexa-express \
  --image-scanning-configuration scanOnPush=true

# Output: Repository URIs
# cortexa-express: 123456789.dkr.ecr.us-east-1.amazonaws.com/cortexa-express
# cortexa-fastapi: 123456789.dkr.ecr.us-east-1.amazonaws.com/cortexa-fastapi
```

### Create RDS PostgreSQL

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name cortexa-subnet-group \
  --db-subnet-group-description "Cortexa DB subnet" \
  --subnet-ids subnet-xxxxx subnet-yyyyy

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier cortexa-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 14.7 \
  --master-username cortexa_admin \
  --master-user-password "UseStrongPassword123!" \
  --allocated-storage 100 \
  --db-subnet-group-name cortexa-subnet-group \
  --vpc-security-group-ids sg-xxxxx \
  --publicly-accessible false \
  --storage-encrypted true \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00" \
  --multi-az true \
  --enable-logging true \
  --log-types postgresql

# Monitor creation (5-10 minutes)
aws rds describe-db-instances \
  --db-instance-identifier cortexa-postgres \
  --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address]'

# Initialize database
PGPASSWORD="UseStrongPassword123!" psql -h cortexa-postgres.xxxxx.us-east-1.rds.amazonaws.com \
  -U cortexa_admin -d postgres < scripts/init_database.sql
```

### Deploy with ECS

**File: `infra/terraform/ecs.tf`**

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "cortexa" {
  name = "cortexa-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Express API Task Definition
resource "aws_ecs_task_definition" "express" {
  family                   = "cortexa-express"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([{
    name      = "express"
    image     = "${aws_ecr_repository.express.repository_url}:latest"
    essential = true
    portMappings = [{
      containerPort = 3000
      hostPort      = 3000
      protocol      = "tcp"
    }]
    environment = [
      { name = "NODE_ENV", value = "production" },
      { name = "Database_HOST", value = aws_db_instance.postgres.address },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379" }
    ]
    secrets = [
      { name = "DATABASE_PASSWORD", valueFrom = aws_secretsmanager_secret.db_password.arn },
      { name = "JWT_SECRET", valueFrom = aws_secretsmanager_secret.jwt_secret.arn }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.express.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# Express API Service
resource "aws_ecs_service" "express" {
  name            = "cortexa-express-service"
  cluster         = aws_ecs_cluster.cortexa.id
  task_definition = aws_ecs_task_definition.express.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.express.arn
    container_name   = "express"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.express]
}

# Auto Scaling
resource "aws_appautoscaling_target" "express_target" {
  max_capacity       = 4
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.cortexa.name}/${aws_ecs_service.express.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "express_cpu" {
  policy_name               = "express-cpu-scaling"
  policy_type               = "TargetTrackingScaling"
  resource_id               = aws_appautoscaling_target.express_target.resource_id
  scalable_dimension        = aws_appautoscaling_target.express_target.scalable_dimension
  service_namespace         = aws_appautoscaling_target.express_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

### Deploy Frontend to S3 + CloudFront

```bash
# Build Next.js application
cd apps/web-app
npm run build
npm run export  # Generate static files

# Create S3 bucket
aws s3 mb s3://cortexa-frontend-prod \
  --region us-east-1

# Configure bucket for static hosting
aws s3api put-bucket-website \
  --bucket cortexa-frontend-prod \
  --website-configuration file://s3-website-config.json

# Upload built files
aws s3 sync out/ s3://cortexa-frontend-prod/ \
  --delete \
  --cache-control "public, max-age=3600" \
  --content-type "text/html" \
  --exclude "*.html" && \
aws s3 cp out/*.html s3://cortexa-frontend-prod/ \
  --content-type "text/html" \
  --cache-control "no-cache"

# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

---

## Domain Configuration

### Route53 Setup

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name cortexa.clinical \
  --caller-reference "$(date +%s)"

# Get nameservers
aws route53 list-hosted-zones-by-name \
  --dns-name cortexa.clinical

# Create A record for frontend
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://route53-changes.json
```

**File: `route53-changes.json`**

```json
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.cortexa.clinical",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d111111abcdef8.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.cortexa.clinical",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "cortexa-alb-123456.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "inference.cortexa.clinical",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "cortexa-alb-inference-123456.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
```

### SSL/TLS Certificate

```bash
# Request certificate from ACM
aws acm request-certificate \
  --domain-name cortexa.clinical \
  --subject-alternative-names "*.cortexa.clinical" \
  --validation-method DNS \
  --region us-east-1

# Verify certificate (DNS validation)
# Copy CNAME record to Route53

# Check certificate status
aws acm list-certificates --region us-east-1
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

**File: `.github/workflows/deploy.yml`**

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main
      - staging

env:
  AWS_REGION: us-east-1
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          npm ci
          pip install -r services/fast-api/requirements.txt

      - name: Run linting
        run: npm run lint

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to ECR
        run: |
          aws ecr get-login-password --region ${{ env.AWS_REGION }} | \
          docker login --username AWS --password-stdin ${{ env.ECR_REGISTRY }}

      - name: Build Express API image
        run: |
          docker build -f infra/docker/express.Dockerfile \
            -t ${{ env.ECR_REGISTRY }}/cortexa-express:${{ github.sha }} \
            -t ${{ env.ECR_REGISTRY }}/cortexa-express:latest .
          docker push ${{ env.ECR_REGISTRY }}/cortexa-express:${{ github.sha }}
          docker push ${{ env.ECR_REGISTRY }}/cortexa-express:latest

      - name: Build FastAPI image
        run: |
          docker build -f infra/docker/fastapi.Dockerfile \
            -t ${{ env.ECR_REGISTRY }}/cortexa-fastapi:${{ github.sha }} \
            -t ${{ env.ECR_REGISTRY }}/cortexa-fastapi:latest .
          docker push ${{ env.ECR_REGISTRY }}/cortexa-fastapi:${{ github.sha }}
          docker push ${{ env.ECR_REGISTRY }}/cortexa-fastapi:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update ECS service - Express
        run: |
          aws ecs update-service \
            --cluster cortexa-cluster \
            --service cortexa-express-service \
            --force-new-deployment \
            --region ${{ env.AWS_REGION }}

      - name: Update ECS service - FastAPI
        run: |
          aws ecs update-service \
            --cluster cortexa-cluster \
            --service cortexa-fastapi-service \
            --force-new-deployment \
            --region ${{ env.AWS_REGION }}

      - name: Wait for service stability
        run: |
          aws ecs wait services-stable \
            --cluster cortexa-cluster \
            --services cortexa-express-service cortexa-fastapi-service \
            --region ${{ env.AWS_REGION }}

      - name: Deploy frontend to S3
        run: |
          cd apps/web-app
          npm run build
          npm run export
          aws s3 sync out/ s3://cortexa-frontend-prod/ --delete

      - name: Invalidate CloudFront cache
        run: |
          DISTRIBUTION_ID=${{ secrets.CF_DISTRIBUTION_ID }}
          aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/*"

      - name: Run smoke tests
        run: |
          npm run test:smoke -- \
            --base-url="https://api.cortexa.clinical"
```

---

## Monitoring & Logging

### CloudWatch Configuration

```bash
# Create log group for Express API
aws logs create-log-group --log-group-name /ecs/cortexa-express

# Create log group for FastAPI
aws logs create-log-group --log-group-name /ecs/cortexa-fastapi

# Set retention policy
aws logs put-retention-policy \
  --log-group-name /ecs/cortexa-express \
  --retention-in-days 30

# Create metric filters
aws logs put-metric-filter \
  --log-group-name /ecs/cortexa-express \
  --filter-name ErrorCount \
  --filter-pattern "[time, request_id, level = ERROR*, ...]" \
  --metric-transformations metricName=ErrorCount,metricNamespace=Cortexa,metricValue=1
```

### Application Performance Monitoring (APM)

**Install Datadog Agent:**

```bash
# Add Datadog to docker-compose.yml
datadog:
  image: datadog/agent:latest
  environment:
    DD_API_KEY: ${DATADOG_API_KEY}
    DD_TRACE_ENABLED: true
    DD_LOGS_ENABLED: true
    DD_METRICS_ENABLED: true
  ports:
    - "8126:8126"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
```

### Application Logging

**File: `services/express-api/src/utils/logger.ts`**

```typescript
import winston from 'winston';
import WinstonCloudWatch from 'winston-cloudwatch';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'express-api' },
  transports: [
    new WinstonCloudWatch({
      logGroupName: '/ecs/cortexa-express',
      logStreamName: `instance-${process.env.HOSTNAME || 'local'}`,
      awsRegion: 'us-east-1',
      messageFormatter: (logEvent) => JSON.stringify(logEvent),
    }),
  ],
});

export default logger;
```

---

## Health Checks & Alerting

### Application Health Check Endpoint

**File: `services/express-api/src/routes/health.ts`**

```typescript
import { Router } from 'express';
import { database } from '../config/database';
import { redis } from '../config/redis';

const router = Router();

router.get('/health', async (req, res) => {
  const health = {
    status: 'UP',
    timestamp: new Date().toISOString(),
    checks: {
      database: 'UP',
      redis: 'UP',
      uptime: process.uptime(),
    },
  };

  try {
    // Check database connection
    await database.query('SELECT 1');
  } catch (error) {
    health.checks.database = 'DOWN';
    health.status = 'PARTIAL';
  }

  try {
    // Check Redis connection
    await redis.ping();
  } catch (error) {
    health.checks.redis = 'DOWN';
    health.status = 'PARTIAL';
  }

  const statusCode = health.status === 'UP' ? 200 : 503;
  res.status(statusCode).json(health);
});

export default router;
```

### CloudWatch Alarms

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cortexa-ecs-high-cpu \
  --alarm-description "Alert when ECS CPU usage is high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789:cortexa-alerts

# Database connection alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cortexa-db-connections-high \
  --alarm-description "Alert when database connections are high" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cortexa-api-errors \
  --alarm-description "Alert on elevated error rates" \
  --metric-name ErrorCount \
  --namespace Cortexa \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### SNS Notifications

```bash
# Create SNS topic
aws sns create-topic --name cortexa-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789:cortexa-alerts \
  --protocol email \
  --notification-endpoint ops@cortexa.clinical

# Subscribe Slack
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789:cortexa-alerts \
  --protocol https \
  --notification-endpoint https://hooks.slack.com/services/XXXXXX/YYYY
```

---

## Disaster Recovery

### Database Backups

```bash
# Automated backups (already configured in RDS)
# - Backup retention: 30 days
# - Multi-AZ: Enabled
# - Backup window: 03:00-04:00 UTC

# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier cortexa-postgres \
  --db-snapshot-identifier cortexa-postgres-backup-$(date +%Y%m%d)

# List backups
aws rds describe-db-snapshots \
  --db-instance-identifier cortexa-postgres
```

### Restore from Backup

```bash
# Restore to new instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier cortexa-postgres-restored \
  --db-snapshot-identifier cortexa-postgres-backup-20260228 \
  --db-instance-class db.t3.medium

# Wait for restoration
aws rds wait db-instance-available \
  --db-instance-identifier cortexa-postgres-restored

# Verify data
PGPASSWORD="password" psql -h cortexa-postgres-restored.xxxxx.us-east-1.rds.amazonaws.com \
  -U cortexa_admin -d cortexa_db -c "SELECT COUNT(*) FROM patient_records;"
```

### Disaster Recovery Plan (RTO: 4 hours, RPO: 1 hour)

```
Infrastructure Failure → Automated Failover (15 min)
                         ↓
                     Database failover to standby
                     (Multi-AZ enabled)
                         ↓
                     ECS service auto-restart
                     (Task replacement)
                         ↓
                     ALB health check recovery
                     ↓
        Application available (15 min total)

Data Loss → Recovery from RDS snapshot (15-30 min)
            ↓
        Restore to new DB instance
        ↓
        Update ECS task to point to restored DB
        ↓
        Restore application state (30 min total)
```

---

## Performance Optimization

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_patient_mrn ON patient_records(patient_mrn);
CREATE INDEX idx_patient_created ON patient_records(created_at DESC);
CREATE INDEX idx_assessment_status ON assessments(status, created_at DESC);

-- Enable query caching (Redis)
SELECT * FROM patient_records WHERE mrn = 'MRN-001' CACHE 300;

-- Connection pooling
-- PgBouncer configuration:
[databases]
cortexa_db = host=cortexa-postgres.xxxxx.rds.amazonaws.com dbname=cortexa_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### API Response Caching

```typescript
// Cache assessment results for 1 hour
router.get('/assessments/:id', async (req, res) => {
  const cacheKey = `assessment:${req.params.id}`;
  
  // Check cache
  const cached = await redis.get(cacheKey);
  if (cached) return res.json(JSON.parse(cached));
  
  // Fetch from DB
  const assessment = await db.assessment.findById(req.params.id);
  
  // Cache for 3600 seconds
  await redis.setex(cacheKey, 3600, JSON.stringify(assessment));
  
  res.json(assessment);
});
```

### CDN Configuration

```bash
# CloudFront cache settings
# - Images: 31536000 seconds (1 year)
# - CSS/JS: 86400 seconds (1 day)
# - HTML: 3600 seconds (1 hour)
# - API: No cache (or very short)

# Enable compression
aws cloudfront update-distribution \
  --distribution-config file://cloudfront-config.json
```

### Database Query Optimization

```sql
-- Use EXPLAIN ANALYZE for query planning
EXPLAIN ANALYZE
SELECT p.*, COUNT(a.id) as assessment_count
FROM patient_records p
LEFT JOIN assessments a ON p.id = a.patient_id
WHERE p.created_at > NOW() - INTERVAL '30 days'
GROUP BY p.id
ORDER BY p.created_at DESC;
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. ECS Service Not Starting

```bash
# Check service events
aws ecs describe-services \
  --cluster cortexa-cluster \
  --services cortexa-express-service | jq '.services[0].events'

# View task logs
aws logs tail /ecs/cortexa-express --follow

# Solution checklist:
# - ✓ ECR image exists and is pulled
# - ✓ Environment variables are set
# - ✓ Database is accessible (check security group)
# - ✓ Container has sufficient resources
# - ✓ Port 3000 is exposed
```

#### 2. Database Connection Timeouts

```bash
# Check RDS security group
aws ec2 describe-security-groups \
  --group-ids sg-xxxxx

# Verify connectivity from ECS
aws ecs execute-command \
  --cluster cortexa-cluster \
  --task cortexa-express-xxx \
  --container express \
  --command "nc -zv cortexa-postgres.xxxxx.rds.amazonaws.com 5432" \
  --interactive

# Solution:
# - Verify inbound rule: port 5432 from ECS security group
# - Check RDS multi-AZ failover status
# - Monitor database connections: SELECT count(*) FROM pg_stat_activity;
```

#### 3. High Memory Usage

```bash
# Check memory metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --statistics Maximum \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300

# Solution:
# - Increase task memory allocation
# - Check for memory leaks in application
# - Enable horizontal scaling
```

#### 4. API Latency Issues

```bash
# Check ALB response times
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --statistics Average \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60

# Profile application
# Add APM instrumentation (Datadog, New Relic)
# Check database query performance
# Review CloudFront cache hit ratio
```

#### 5. Database Migration Issues

```bash
# Check migration status
aws ssm send-command \
  --instance-ids i-xxxxx \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=[
    "psql -h cortexa-postgres -U cortexa_admin -d cortexa_db -c \"SELECT * FROM schema_migrations;\""
  ]'

# Rollback migration
npm run migration:rollback -- --steps=1
```

### Debugging Tools

```bash
# Real-time log streaming
aws logs tail /ecs/cortexa-express --follow --format short

# SSH into container
aws ecs execute-command \
  --cluster cortexa-cluster \
  --task cortexa-express-xxx \
  --container express \
  --interactive --command "/bin/sh"

# Check metrics
aws cloudwatch list-metrics --namespace Cortexa

# Database console
psql -h cortexa-postgres.xxxxx.rds.amazonaws.com -U cortexa_admin -d cortexa_db
\dt  # List tables
\d+ patient_records  # Describe table
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review approved
- [ ] Security scan passed (no critical vulnerabilities)
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] SSL certificates valid
- [ ] Backup system functional

### Deployment

- [ ] CI/CD pipeline successful
- [ ] Docker images built and pushed
- [ ] ECS services updated
- [ ] Health checks passing
- [ ] Frontend deployed to S3
- [ ] CloudFront cache invalidated
- [ ] DNS records verified

### Post-Deployment

- [ ] Smoke tests passed
- [ ] Monitoring alerts configured
- [ ] Error rates normal
- [ ] Database queries optimized
- [ ] API response times acceptable
- [ ] Certificate validity confirmed
- [ ] Backup verification completed

---

**Last Updated**: February 28, 2026  
**Deployment Status**: Under Development
**SLA Target**: 99.9% Uptime
