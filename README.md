# Microservice Delivery Pipeline 🚀

A production-grade CI/CD implementation for a FastAPI Microservice. This repository demonstrates the automation of the entire Software Development Lifecycle (SDLC) from code commit to cloud artifact.

## 🔄 The Pipeline Flow
1.  **Continuous Integration:** GitHub Actions runner spins up, installs dependencies, and executes `pytest` suites.
2.  **Containerization:** Upon passing tests, builds an optimized Docker image (Multi-stage build).
3.  **Continuous Delivery:** Authenticates via OIDC/Secrets and pushes the artifact to a private **AWS ECR** registry.

## 🔧 Engineering Standards
- **Validation:** Pydantic models ensure strict data typing for API payloads.
- **Testing:** Comprehensive unit tests using `TestClient` and `Pytest`.
- **Security:** Zero-trust credential management using GitHub Secrets.
- **Networking:** App bound to `0.0.0.0` for containerized ingress traffic.
