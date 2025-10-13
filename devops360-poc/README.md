
---

## 🚀 Deployment Flow

1. **CI/CD Trigger**: Push to `main` branch starts GitHub Actions.
2. **Lock Check**: Prevents concurrent deployments using a lock API.
3. **App Deployment**: Code is copied to EC2 and started via `pm2`.
4. **Notifications**: SNS alerts on success or failure.
5. **Lock Release**: Always released at the end of the workflow.

---

## 🧱 Infrastructure Overview

Defined in `infra/devops360-stack.yaml` using AWS CloudFormation:

### DynamoDB Table

- **Name**: `DevOps360_Locks`
- **Primary Key**: `env` (String)
- **Billing Mode**: Pay-per-request

### SNS Topic

- **Name**: `DevOps360Alerts`

### Outputs

- `LocksTableName`: Reference to DynamoDB table
- `SNSTopicArn`: Reference to SNS topic

---

## ⚙️ GitHub Actions Workflow

Located at `.github/workflows/deploy.yml`, this workflow:

- Installs dependencies and runs tests
- Checks and acquires environment lock
- Deploys app to EC2 via SSH and `pm2`
- Publishes SNS alerts on success or failure
- Releases lock regardless of outcome

---

## 🔐 Lock API Endpoints

These endpoints are used to manage deployment locks and simulate auto-heal triggers.

### Acquire Lock (Manual)

```bash
# Acquire Lock
curl -X POST "${LOCK_API_URL}/env-lock" \
  -H "Content-Type: application/json" \
  -d '{"user":"demo-user"}'

# Check Lock
curl "${LOCK_API_URL}/env-lock-check"

# Release Lock
curl -X DELETE "${LOCK_API_URL}/env-lock"

# Simulate Auto-Heal Trigger
curl -X POST "${LOCK_API_URL}/analyze-log" \
  -H "Content-Type: application/json" \
  -d '{"log":"OutOfMemoryError: JavaScript heap out of memory"}'

# App Health Check
curl http://<EC2_PUBLIC_IP>:8080/health



Let me know if you'd like this saved as a file or want to add setup instructions for the Lambda function or EC2 provisioning!