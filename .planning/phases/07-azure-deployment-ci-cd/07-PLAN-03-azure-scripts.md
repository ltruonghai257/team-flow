---
plan: "07-03"
wave: 2
phase: 7
title: "Azure Provisioning & Deploy Scripts"
depends_on:
  - "07-02"
files_modified:
  - scripts/setup-azure.sh
  - scripts/deploy.sh
autonomous: true
requirements_addressed:
  - REQ-05a
  - REQ-05c
---

# Plan 07-03: Azure Provisioning & Deploy Scripts

## Objective

Create two shell scripts for Azure resource management:

1. **`scripts/setup-azure.sh`** — one-time provisioning: resource group, ACR, App Service plan,
   App Service (with managed identity + AcrPull), PostgreSQL Flexible Server
2. **`scripts/deploy.sh`** — manual deploy: builds monolith image via `az acr build`, updates
   App Service container image, restarts the app

## Context (from CONTEXT.md decisions)

- **D-06**: Single App Service (Linux, B1 SKU) — one monolith container
- **D-07**: Azure Container Registry (ACR) stores images
- **D-08**: Azure PostgreSQL Flexible Server — `DATABASE_URL` via env var
- **D-09**: Scripts use variables at top — configurable before first run, no hard-coded names
- **D-10**: Default region: `westus2`
- **D-11**: Images tagged with git commit SHA (`teamflow:$COMMIT_SHA`) — no `:latest` in production
- **D-23**: `setup-azure.sh` — full one-time provisioning
- **D-24**: `deploy.sh` — manual deploy via `az acr build` + App Service update

## Tasks

### Task 1: Create scripts directory and setup-azure.sh

<read_first>
- `.planning/REQUIREMENTS.md` REQ-05a — infrastructure requirements (ACR, App Service B1, PostgreSQL Flexible Server)
- `backend/app/config.py` — env var names: `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT`, `ALLOWED_ORIGINS`, `COOKIE_SECURE`, `AI_MODEL`
- `backend/.env.example` — field names reference
</read_first>

<action>
Create `scripts/setup-azure.sh` with the following content (variables at top per D-09):

```bash
#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# TeamFlow — One-time Azure Resource Provisioning
# Edit variables below before running.
# Run once per environment. Idempotent for most resources.
# ─────────────────────────────────────────────

# ── Configurable Variables ────────────────────
RG="teamflow-rg"
LOCATION="westus2"
ACR_NAME="teamflowacr"          # Must be globally unique, lowercase alphanumeric
APP_SERVICE_PLAN="teamflow-plan"
APP_NAME="teamflow-app"         # Must be globally unique → https://$APP_NAME.azurewebsites.net
DB_SERVER_NAME="teamflow-db"    # Must be globally unique
DB_ADMIN_USER="teamflowadmin"
DB_ADMIN_PASS=""                # Set before running: export DB_ADMIN_PASS="..."
DB_NAME="teamflow"
SKU_APP_SERVICE="B1"
SKU_DB="Standard_B1ms"
# ─────────────────────────────────────────────

if [[ -z "$DB_ADMIN_PASS" ]]; then
  echo "ERROR: Set DB_ADMIN_PASS before running: export DB_ADMIN_PASS='your-password'"
  exit 1
fi

echo "==> Logging in to Azure..."
az account show > /dev/null 2>&1 || az login

echo "==> Creating resource group: $RG in $LOCATION"
az group create --name "$RG" --location "$LOCATION"

echo "==> Creating Azure Container Registry: $ACR_NAME"
az acr create --name "$ACR_NAME" --resource-group "$RG" --sku Basic --admin-enabled false

echo "==> Creating App Service plan: $APP_SERVICE_PLAN (Linux, $SKU_APP_SERVICE)"
az appservice plan create \
  --name "$APP_SERVICE_PLAN" \
  --resource-group "$RG" \
  --is-linux \
  --sku "$SKU_APP_SERVICE"

echo "==> Creating App Service: $APP_NAME"
az webapp create \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --plan "$APP_SERVICE_PLAN" \
  --container-image-name "mcr.microsoft.com/appsvc/staticsite:latest"

echo "==> Assigning managed identity to App Service"
az webapp identity assign \
  --name "$APP_NAME" \
  --resource-group "$RG"

echo "==> Granting App Service AcrPull on ACR"
PRINCIPAL_ID=$(az webapp identity show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query principalId \
  --output tsv)
ACR_ID=$(az acr show \
  --name "$ACR_NAME" \
  --resource-group "$RG" \
  --query id \
  --output tsv)
az role assignment create \
  --assignee "$PRINCIPAL_ID" \
  --role AcrPull \
  --scope "$ACR_ID"

echo "==> Configuring App Service to use ACR managed identity"
az webapp config set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --generic-configurations '{"acrUseManagedIdentityCreds": true}'

echo "==> Creating PostgreSQL Flexible Server: $DB_SERVER_NAME"
az postgres flexible-server create \
  --name "$DB_SERVER_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --admin-user "$DB_ADMIN_USER" \
  --admin-password "$DB_ADMIN_PASS" \
  --sku-name "$SKU_DB" \
  --tier Burstable \
  --version 16 \
  --yes

echo "==> Creating database: $DB_NAME"
az postgres flexible-server db create \
  --resource-group "$RG" \
  --server-name "$DB_SERVER_NAME" \
  --database-name "$DB_NAME"

echo "==> Allowing App Service outbound IPs to connect to PostgreSQL"
OUTBOUND_IPS=$(az webapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query outboundIpAddresses \
  --output tsv)
IFS=',' read -ra IPS <<< "$OUTBOUND_IPS"
for IP in "${IPS[@]}"; do
  az postgres flexible-server firewall-rule create \
    --resource-group "$RG" \
    --name "$DB_SERVER_NAME" \
    --rule-name "appservice-${IP//./-}" \
    --start-ip-address "$IP" \
    --end-ip-address "$IP" 2>/dev/null || true
done

DB_HOST="$DB_SERVER_NAME.postgres.database.azure.com"
DATABASE_URL="postgresql+asyncpg://$DB_ADMIN_USER:$DB_ADMIN_PASS@$DB_HOST:5432/$DB_NAME?ssl=require"

echo ""
echo "==> Setting App Service application settings"
echo "    (SECRET_KEY and AI keys must be updated manually in Azure Portal or via az webapp config appsettings set)"
az webapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    DATABASE_URL="$DATABASE_URL" \
    ENVIRONMENT="production" \
    ALLOWED_ORIGINS="https://$APP_NAME.azurewebsites.net" \
    COOKIE_SECURE="True" \
    WEBSITES_PORT="80" \
    SECRET_KEY="REPLACE_WITH_SECURE_KEY" \
    AI_MODEL="gpt-4o" \
    OPENAI_API_KEY="REPLACE_WITH_KEY"

echo ""
echo "════════════════════════════════════════════════"
echo " Azure resources provisioned successfully!"
echo "════════════════════════════════════════════════"
echo " App URL:     https://$APP_NAME.azurewebsites.net"
echo " ACR:         $ACR_NAME.azurecr.io"
echo " DB Host:     $DB_HOST"
echo ""
echo " NEXT STEPS:"
echo "  1. Update SECRET_KEY in Azure Portal → App Service → Configuration"
echo "  2. Update OPENAI_API_KEY (or ANTHROPIC_API_KEY) in App Settings"
echo "  3. Run scripts/deploy.sh to build and deploy the first image"
echo "════════════════════════════════════════════════"
```
</action>

<acceptance_criteria>
- `scripts/setup-azure.sh` exists
- File is executable (`chmod +x scripts/setup-azure.sh` run after creation, or permissions set in script header)
- File contains configurable variables at top: `RG`, `LOCATION`, `ACR_NAME`, `APP_SERVICE_PLAN`, `APP_NAME`, `DB_SERVER_NAME`
- File contains `az group create`
- File contains `az acr create`
- File contains `az appservice plan create --is-linux`
- File contains `az webapp create`
- File contains `az webapp identity assign` and `az role assignment create` with `AcrPull`
- File contains `az postgres flexible-server create`
- File contains `az webapp config appsettings set` with `DATABASE_URL`, `ENVIRONMENT`, `ALLOWED_ORIGINS`
- File contains guard: `if [[ -z "$DB_ADMIN_PASS" ]]`
</acceptance_criteria>

---

### Task 2: Create deploy.sh manual deploy script

<read_first>
- `scripts/setup-azure.sh` — variable names to keep consistent (ACR_NAME, APP_NAME, RG)
- `Dockerfile` — at repo root (context path for `az acr build`)
</read_first>

<action>
Create `scripts/deploy.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# TeamFlow — Manual Deploy Script
# Builds monolith image via ACR and deploys to App Service.
# Run from the repo root directory.
# ─────────────────────────────────────────────

# ── Configurable Variables ────────────────────
RG="teamflow-rg"
ACR_NAME="teamflowacr"
APP_NAME="teamflow-app"
# ─────────────────────────────────────────────

COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${ACR_NAME}.azurecr.io/teamflow:${COMMIT_SHA}"

echo "==> Logging in to Azure..."
az account show > /dev/null 2>&1 || az login

echo "==> Building image via ACR: teamflow:$COMMIT_SHA"
echo "    (Build runs in Azure — no local Docker daemon required)"
az acr build \
  --registry "$ACR_NAME" \
  --image "teamflow:${COMMIT_SHA}" \
  .

echo "==> Deploying to App Service: $APP_NAME"
az webapp config container set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --container-image-name "$IMAGE_TAG"

echo "==> Restarting App Service to apply new image"
az webapp restart \
  --name "$APP_NAME" \
  --resource-group "$RG"

echo ""
echo "════════════════════════════════════════════════"
echo " Deployed: teamflow:$COMMIT_SHA"
echo " App URL:  https://$APP_NAME.azurewebsites.net"
echo "════════════════════════════════════════════════"
```

Make both scripts executable:
```bash
chmod +x scripts/setup-azure.sh scripts/deploy.sh
```
</action>

<acceptance_criteria>
- `scripts/deploy.sh` exists
- File contains configurable variables `RG`, `ACR_NAME`, `APP_NAME` at top
- File contains `COMMIT_SHA=$(git rev-parse --short HEAD)`
- File contains `az acr build --registry "$ACR_NAME" --image "teamflow:${COMMIT_SHA}" .`
- File contains `az webapp config container set` with `--container-image-name "$IMAGE_TAG"`
- File contains `az webapp restart`
- File does NOT use `:latest` tag (commit SHA only, per D-11)
- `scripts/setup-azure.sh` and `scripts/deploy.sh` are executable (`ls -la scripts/` shows `x` bit)
</acceptance_criteria>

---

## Verification Criteria

- [ ] `scripts/setup-azure.sh` exists with all required `az` commands and variables at top
- [ ] `scripts/deploy.sh` exists, uses `git rev-parse --short HEAD` for image tag (no `:latest`)
- [ ] Both scripts have executable permissions
- [ ] `bash -n scripts/setup-azure.sh` exits 0 (syntax check)
- [ ] `bash -n scripts/deploy.sh` exits 0 (syntax check)

## must_haves

- Variables at top of each script (D-09) — no hard-coded names in command bodies
- `setup-azure.sh` provisions all resources needed: ACR, App Service plan, App Service, PostgreSQL Flexible Server
- App Service gets managed identity + AcrPull role so it can pull images without stored credentials
- `deploy.sh` uses `az acr build` (cloud build — no local Docker daemon required)
- No `:latest` tag in production — commit SHA only (D-11)

## threat_model

| Threat | Mitigation |
|--------|-----------|
| `DB_ADMIN_PASS` in shell history | Script requires env var (`export DB_ADMIN_PASS=...`), not CLI arg |
| `SECRET_KEY` placeholder deployed to production | Script sets `REPLACE_WITH_SECURE_KEY`; README instructs updating before first deploy |
| Service principal credentials stored in scripts | Not stored — uses `az login` interactive or GitLab CI vars for CI; managed identity for App Service→ACR |
| Firewall rule creation failure silently ignored | `|| true` on firewall rules is intentional — some IPs may already exist; all IPs are iterated |
