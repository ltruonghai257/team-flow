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
