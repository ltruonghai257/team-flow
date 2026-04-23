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
