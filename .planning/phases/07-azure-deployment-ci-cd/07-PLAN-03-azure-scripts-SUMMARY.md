# Summary: Plan 07-03 — Azure Provisioning & Deploy Scripts

**Status:** Complete  
**Completed:** 2026-04-23

## What Was Done

- Created `scripts/setup-azure.sh`: one-time provisioning of resource group, ACR, App Service plan, App Service with managed identity + AcrPull, PostgreSQL Flexible Server, firewall rules, and App Settings
- Created `scripts/deploy.sh`: manual deploy via `az acr build` tagged with git commit SHA, updates App Service container and restarts
- Both scripts: variables at top (RG, ACR_NAME, APP_NAME, etc.), executable, pass `bash -n` syntax check

## Deviations

None.

## Verification

- [x] `scripts/setup-azure.sh` exists with `az group create`, `az acr create`, `az appservice plan create --is-linux`, `az webapp create`, `az webapp identity assign`, `az role assignment create` with AcrPull, `az postgres flexible-server create`, `az webapp config appsettings set`
- [x] `scripts/deploy.sh` uses `COMMIT_SHA=$(git rev-parse --short HEAD)` — no `:latest` tag
- [x] Both scripts executable (`ls -la scripts/` shows `x` bit)
- [x] `bash -n scripts/setup-azure.sh` exits 0
- [x] `bash -n scripts/deploy.sh` exits 0
