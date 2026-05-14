# Microservice Delivery Pipeline

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=githubactions)
![AWS ECR](https://img.shields.io/badge/AWS-ECR-232F3E?style=for-the-badge&logo=amazon-aws)
![AWS App Runner](https://img.shields.io/badge/AWS-App_Runner-232F3E?style=for-the-badge&logo=amazon-aws)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)

A CI/CD pipeline for a FastAPI microservice. Two workflows enforce
a clean separation between test feedback and production delivery,
with progressive deployment through staging → smoke tests → production.

---

## Pipeline architecture

```
dev / feature branches              main branch
        │                                │
        ▼                                ▼
  ci-dev.yml                       pipeline.yml
        │                                │
        │                                ▼
        │           ┌────────────────────────────────┐
        │           │ 1. test-and-build              │
        │           │    pytest → docker → ECR push  │
        │           └────────────────┬───────────────┘
        │                            ▼
        │           ┌────────────────────────────────┐
        │           │ 2. deploy-staging              │
        │           │    App Runner redeploy         │
        │           │    (microservice-staging)      │
        │           └────────────────┬───────────────┘
        │                            ▼
        │           ┌────────────────────────────────┐
        │           │ 3. smoke-tests                 │
        │           │    curl / and POST /metrics    │
        │           └────────────────┬───────────────┘
        │                            ▼
        │                  ◆ manual approval ◆
        │                            ▼
        │           ┌────────────────────────────────┐
        │           │ 4. deploy-prod                 │
        │           │    App Runner redeploy         │
        │           │    (microservice-prod)         │
        │           └────────────────────────────────┘
        ▼
  pytest only
  no credentials
  fast feedback
```

PRs targeting main also trigger `ci-dev.yml` — tests must
pass before any merge.

---

## Workflows

### ci-dev.yml — CI for dev branches
Triggers on all pushes except main, and on pull requests to main.
Runs pytest with `--tb=short -v` for clean output. No AWS
credentials required — dev branches get test feedback without
production access.

### pipeline.yml — Full CD pipeline for main
Triggers on push to main. Four sequential jobs, each gated on the
previous:

1. **test-and-build** — pytest, then docker build, then ECR push
   (image tagged with commit SHA + `latest`)
2. **deploy-staging** — `aws apprunner start-deployment` against the
   staging service, poll until status returns to `RUNNING`
3. **smoke-tests** — public curl against the staging URL; verifies
   `/` returns `running` and `POST /metrics` returns `Data Received`.
   No AWS credentials — purely external
4. **deploy-prod** — gated by GitHub Environment `production`
   (manual approval). Resolves the prod service ARN by name, triggers
   redeploy, polls until `RUNNING`

---

## App Runner services

| Service                | Stage   | URL                                              |
| ---------------------- | ------- | ------------------------------------------------ |
| `microservice-staging` | Staging | https://mp2tqrd5x4.us-east-1.awsapprunner.com    |
| `microservice-prod`    | Prod    | https://29afs6f827.us-east-1.awsapprunner.com    |

Both services pull from the same ECR repository (`cloud-projects`).
ECR push triggers redeploy via `start-deployment` rather than App
Runner's auto-deploy, so the pipeline controls promotion order.

---

## Manual approval gate

`deploy-prod` declares `environment: production`. GitHub blocks the
job until a configured reviewer approves it in the Actions UI.

To configure:
**Repo Settings → Environments → `production` → Required reviewers**.

Without reviewers configured, the gate is a no-op and prod deploys
auto-promote — set this up before relying on the gate.

---

## A note on App Runner

AWS stopped accepting new App Runner customers in April 2026.
Existing services continue to run, but this exact stack will not
be reproducible on new AWS accounts.

The pipeline shape — build → push → trigger managed-service redeploy
→ smoke test → gated prod — transfers cleanly to other targets.
Only the deploy step changes:

- **AWS ECS with Express Mode** — swap `aws apprunner start-deployment`
  for `aws ecs update-service --force-new-deployment`
- **Google Cloud Run** — swap for `gcloud run deploy --image <tag>`

The four-stage structure, the smoke-test gate, and the manual-approval
gate stay identical.

---

## Security model

AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
are stored as GitHub Secrets and injected only at runtime.
The workflow files are public — hardcoding credentials would
expose them to anyone who clones the repo.

The IAM user behind those secrets requires:
- `ecr:*` (build & push)
- `apprunner:StartDeployment`, `apprunner:DescribeService`,
  `apprunner:ListServices` (deploy & poll)

---

## Engineering standards

**Validation:** Pydantic models enforce strict typing on all API payloads.
**Testing:** Unit tests via pytest + FastAPI TestClient.
**Containerization:** Docker image built for `linux/amd64`.
**Artifact tagging:** Images tagged with the commit SHA (`${{ github.sha }}`)
for full traceability — every image maps to an exact commit.

---

## Local development
```bash
pip install -r requirements.txt
pip install pytest httpx
python -m pytest --tb=short -v
```
