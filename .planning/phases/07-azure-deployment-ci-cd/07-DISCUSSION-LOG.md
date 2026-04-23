# Phase 7: Azure Deployment & CI/CD - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 07-azure-deployment-ci-cd
**Areas discussed:** Azure resource naming, Frontend hosting target, CI/CD trigger & strategy, Env config scope

---

## Azure Resource Naming

| Option | Description | Selected |
|--------|-------------|----------|
| Variables at the top | Scripts define RG, ACR_NAME, BACKEND_APP, FRONTEND_APP etc. as vars at top | ✓ |
| Bake in 'teamflow-*' names | Hard-code names like teamflow-rg, teamflow-acr throughout | |

**User's choice:** Variables at the top

| Option | Description | Selected |
|--------|-------------|----------|
| eastus | Cheapest and most widely available | |
| southeastasia | Better latency for SE Asia teams | |
| Leave as variable | User must set LOCATION before running | |

**User's choice:** `westus2` (free text — specific region requested)

---

## Frontend Hosting Target

| Option | Description | Selected |
|--------|-------------|----------|
| Azure App Service container | Consistent with backend, supports SSR, ~$13/month B1 SKU | Initially selected |
| Azure Static Web Apps | Free tier, CDN-backed, but requires adapter-static | |

**Note:** User subsequently redirected to monolith architecture (single container, nginx). This area was superseded by the architecture change.

---

## CI/CD Trigger & Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Push-to-main + manual dispatch | workflow_dispatch trigger for redeployment without commit | ✓ |
| Push-to-main only | Simpler, fallback via deploy.sh | |

**User's choice:** Push-to-main + manual dispatch

| Option | Description | Selected |
|--------|-------------|----------|
| Parallel builds | Two jobs, cuts pipeline time in half | ✓ |
| Sequential single job | Simpler YAML, slightly slower | |

**User's choice:** Parallel builds

| Option | Description | Selected |
|--------|-------------|----------|
| git SHA tag only | Exact traceability, no ambiguous :latest in CI | ✓ |
| latest tag only | Simpler but no rollback | |
| Both SHA and latest | Traceability + convenience | |

**User's choice:** git SHA tag only

| Option | Description | Selected |
|--------|-------------|----------|
| No health check (v1) | Azure deployment success is sufficient | ✓ |
| curl health check | Smoke test gate post-deploy | |

**User's choice:** No health check for v1

**Architecture pivot (free text):** User stated: "I want application follow monolith architecture, using nginx and we use gitlab"

This changed:
- From two separate App Services → one monolith container
- From GitHub Actions → GitLab CI/CD
- Opened new sub-areas: container structure, nginx routing, SvelteKit adapter, process management

| Option | Description | Selected |
|--------|-------------|----------|
| Multi-stage Dockerfile (monolith) | Bun build → Python deps → final image with nginx + supervisord | ✓ |
| Separate Dockerfiles + docker-compose | Keep existing Dockerfiles, nginx as 3rd service | |

**User's choice:** Multi-stage Dockerfile

| Option | Description | Selected |
|--------|-------------|----------|
| supervisord | Managed process supervisor, handles crash restarts | ✓ |
| entrypoint shell script | Simpler, no restart on crash | |
| You decide | Claude picks | |

**User's choice:** supervisord

| Option | Description | Selected |
|--------|-------------|----------|
| /api/* and /ws/* → uvicorn; else → static | Standard SPA pattern | ✓ |
| You decide | Claude designs nginx config | |

**User's choice:** /api/* and /ws/* → uvicorn; everything else → SvelteKit static

| Option | Description | Selected |
|--------|-------------|----------|
| Switch to adapter-static | Pure static output, no Node process, simpler | ✓ |
| Keep adapter-node as 3rd process | Preserves SSR but adds complexity | |

**User's choice:** Switch to adapter-static

| Option | Description | Selected |
|--------|-------------|----------|
| gitlab.com (SaaS) | Standard hosted GitLab | |
| Self-hosted GitLab | On-premise instance | ✓ |
| You decide | Doesn't matter for YAML structure | |

**User's choice:** Self-hosted GitLab

| Option | Description | Selected |
|--------|-------------|----------|
| Service principal credentials as GitLab CI variables | az login --service-principal in pipeline | ✓ |
| Azure managed identity (runner on Azure VM) | Zero-credential if runner is Azure VM | |

**User's choice:** Service principal credentials

---

## Env Config Scope

| Option | Description | Selected |
|--------|-------------|----------|
| None — relative paths /api/* | No build-time env vars needed | ✓ |
| PUBLIC_API_URL baked in | Explicit API origin at build time | |

**User's choice:** None — all API calls use relative paths

| Option | Description | Selected |
|--------|-------------|----------|
| Wildcard placeholder with instructions | https://YOUR_APP.azurewebsites.net + README note | ✓ |
| Real teamflow.azurewebsites.net URL | Bake in the actual URL | |
| You decide | Claude sets sensible defaults | |

**User's choice:** Wildcard placeholder with instructions

---

## Claude's Discretion

- Dockerfile base image for final stage
- supervisord config structure
- nginx worker settings
- GitLab CI runner image
- Whether setup-azure.sh creates DB or notes it as separate step
