---
plan: "07-04"
wave: 2
phase: 7
title: "GitLab CI/CD Pipeline"
depends_on:
  - "07-02"
files_modified:
  - .gitlab-ci.yml
autonomous: true
requirements_addressed:
  - REQ-05b
---

# Plan 07-04: GitLab CI/CD Pipeline

## Objective

Create `.gitlab-ci.yml` at the repo root to automate build and deploy on push to `main`.
Pipeline uses a single job with `mcr.microsoft.com/azure-cli` image: logs in via service principal,
builds the monolith image via `az acr build`, then deploys to Azure App Service.

## Context (from CONTEXT.md decisions)

- **D-12**: Pipeline file: `.gitlab-ci.yml` at repo root
- **D-13**: Self-hosted GitLab instance
- **D-14**: Azure auth via service principal credentials stored as masked GitLab CI/CD variables
- **D-15**: Push to `main` trigger + manual deploy option (`when: manual`)
- **D-16**: Sequential stages: build → deploy (one image, no parallel needed)
- **D-17**: No health check / deploy gate for v1 — App Service deployment success is sufficient
- **D-11**: Images tagged with `$CI_COMMIT_SHORT_SHA` only (no `:latest`)

## Tasks

### Task 1: Create .gitlab-ci.yml

<read_first>
- `scripts/deploy.sh` — `az acr build` and `az webapp config container set` commands (same logic)
- `scripts/setup-azure.sh` — variable names: `RG`, `ACR_NAME`, `APP_NAME`
- `Dockerfile` — at repo root (build context is `.`)
</read_first>

<action>
Create `.gitlab-ci.yml` at the repo root with:

```yaml
# TeamFlow GitLab CI/CD Pipeline
# Triggers on push to main branch.
# Required GitLab CI/CD variables (Settings → CI/CD → Variables, all masked):
#   AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID
#   ACR_NAME     — e.g. teamflowacr
#   APP_NAME     — e.g. teamflow-app
#   RG           — e.g. teamflow-rg

stages:
  - build
  - deploy

variables:
  IMAGE_TAG: "$CI_COMMIT_SHORT_SHA"

build:
  stage: build
  image: mcr.microsoft.com/azure-cli
  script:
    - az login --service-principal
        --username "$AZURE_CLIENT_ID"
        --password "$AZURE_CLIENT_SECRET"
        --tenant "$AZURE_TENANT_ID"
    - az account set --subscription "$AZURE_SUBSCRIPTION_ID"
    - echo "==> Building image teamflow:$IMAGE_TAG via ACR (cloud build)"
    - az acr build
        --registry "$ACR_NAME"
        --image "teamflow:$IMAGE_TAG"
        .
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

deploy:
  stage: deploy
  image: mcr.microsoft.com/azure-cli
  script:
    - az login --service-principal
        --username "$AZURE_CLIENT_ID"
        --password "$AZURE_CLIENT_SECRET"
        --tenant "$AZURE_TENANT_ID"
    - az account set --subscription "$AZURE_SUBSCRIPTION_ID"
    - echo "==> Deploying teamflow:$IMAGE_TAG to App Service $APP_NAME"
    - az webapp config container set
        --name "$APP_NAME"
        --resource-group "$RG"
        --container-image-name "$ACR_NAME.azurecr.io/teamflow:$IMAGE_TAG"
    - az webapp restart
        --name "$APP_NAME"
        --resource-group "$RG"
    - echo "Deployed https://$APP_NAME.azurewebsites.net @ $IMAGE_TAG"
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success
  needs:
    - build

# Manual deploy: trigger a deploy from any branch without pushing to main.
# Go to GitLab → CI/CD → Pipelines → Run pipeline → this job will appear as manually triggerable.
deploy_manual:
  stage: deploy
  image: mcr.microsoft.com/azure-cli
  script:
    - az login --service-principal
        --username "$AZURE_CLIENT_ID"
        --password "$AZURE_CLIENT_SECRET"
        --tenant "$AZURE_TENANT_ID"
    - az account set --subscription "$AZURE_SUBSCRIPTION_ID"
    - echo "==> Manual deploy: teamflow:$IMAGE_TAG to $APP_NAME"
    - az webapp config container set
        --name "$APP_NAME"
        --resource-group "$RG"
        --container-image-name "$ACR_NAME.azurecr.io/teamflow:$IMAGE_TAG"
    - az webapp restart
        --name "$APP_NAME"
        --resource-group "$RG"
  rules:
    - when: manual
      allow_failure: true
```
</action>

<acceptance_criteria>
- `.gitlab-ci.yml` exists at repo root
- File contains `stages:` with `build` and `deploy`
- File contains `image: mcr.microsoft.com/azure-cli` in both jobs
- File contains `az login --service-principal` with `$AZURE_CLIENT_ID`, `$AZURE_CLIENT_SECRET`, `$AZURE_TENANT_ID`
- File contains `az acr build --registry "$ACR_NAME" --image "teamflow:$IMAGE_TAG" .`
- File contains `az webapp config container set --name "$APP_NAME"`
- File contains `az webapp restart`
- File contains `rules:` with `$CI_COMMIT_BRANCH == "main"` (not deprecated `only:`)
- File contains `needs: [build]` on the deploy job (DAG dependency)
- File contains `deploy_manual` job with `when: manual`
- File does NOT contain `:latest` image tag
- `python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))"` exits 0 (valid YAML)
</acceptance_criteria>

---

### Task 2: Add GitLab runner configuration note to .gitlab-ci.yml

<read_first>
- `.gitlab-ci.yml` — just created
</read_first>

<action>
Verify the pipeline uses `mcr.microsoft.com/azure-cli` image for both jobs — this means the
self-hosted GitLab runner only needs to support Docker executor (no privileged mode, no
Docker-in-Docker). `az acr build` sends the build context to Azure and builds in the cloud,
so the runner never runs Docker itself.

The `.gitlab-ci.yml` already reflects this approach. No changes needed — this task is a
verification checkpoint.

Confirm: neither job uses `services: [docker:dind]` or requires `privileged: true`.
</action>

<acceptance_criteria>
- `.gitlab-ci.yml` does NOT contain `docker:dind`
- `.gitlab-ci.yml` does NOT contain `privileged: true`
- Both `build` and `deploy` jobs use `image: mcr.microsoft.com/azure-cli`
</acceptance_criteria>

---

## Verification Criteria

- [ ] `.gitlab-ci.yml` exists at repo root with valid YAML syntax
- [ ] Two jobs: `build` (stage: build) and `deploy` (stage: deploy)
- [ ] `deploy` job has `needs: [build]` (waits for build before deploying)
- [ ] Both jobs trigger only on `main` branch push
- [ ] Image tagged with `$CI_COMMIT_SHORT_SHA` — no `:latest`
- [ ] Service principal login uses 4 masked variables: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
- [ ] No Docker-in-Docker required — `az acr build` handles cloud build

## must_haves

- Pipeline triggers on push to `main` (D-15)
- Image tagged with commit SHA, not `:latest` (D-11)
- Service principal auth via GitLab CI/CD masked variables (D-14)
- `az acr build` used for cloud build (no Docker daemon on runner needed)
- Deploy job depends on successful build job

## threat_model

| Threat | Mitigation |
|--------|-----------|
| `AZURE_CLIENT_SECRET` exposed in logs | GitLab masked variable — never printed in job output |
| Deploying broken build | `deploy` job has `needs: [build]` + `when: on_success` — deploy only runs if build succeeds |
| Stale image deployed (wrong SHA) | `IMAGE_TAG: "$CI_COMMIT_SHORT_SHA"` — always the current commit |
| Service principal has excessive permissions | Should have: `Contributor` on resource group only (or `AcrPush` on ACR + `Contributor` on App Service) |
