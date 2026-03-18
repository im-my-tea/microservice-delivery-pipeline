# Microservice Delivery Pipeline

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=githubactions)
![AWS ECR](https://img.shields.io/badge/AWS-ECR-232F3E?style=for-the-badge&logo=amazon-aws)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)

A CI/CD pipeline for a FastAPI microservice. Two workflows enforce 
a clean separation between test feedback and production delivery.

---

## Pipeline architecture
```
dev / feature branches          main branch
        │                            │
        ▼                            ▼
  ci-dev.yml                   pipeline.yml
        │                            │
  pytest only                  pytest
  no credentials               → docker build
  no Docker                    → ECR push
  fast feedback                → production artifact
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
Triggers on push to main. Full sequence: pytest → Docker build → 
ECR push. Uses GitHub Secrets for AWS credentials — never 
hardcoded in the workflow file.

---

## Security model

AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) 
are stored as GitHub Secrets and injected only at runtime. 
The workflow files are public — hardcoding credentials would 
expose them to anyone who clones the repo.

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