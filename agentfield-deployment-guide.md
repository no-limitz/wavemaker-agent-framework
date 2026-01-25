# AgentField Agent Deployment Guide for Coolify

## Overview

This guide covers deploying AgentField agents on Coolify with proper networking, proxy configuration, and control plane connectivity.

---

## Quick Reference

| Setting | Value |
|---------|-------|
| Control Plane URL | `http://agentfield:8080` |
| Predefined Network | `coolify` |
| Internal Port | Must match container's listening port |
| Proxy Port | Use **internal** port, not host-mapped port |

---

## Step 1: Docker Compose Configuration

```yaml
services:
  my-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: my-agent
    environment:
      # AgentField Configuration (REQUIRED)
      - AGENTFIELD_CONTROL_PLANE_URL=http://agentfield:8080
      - AGENT_CALLBACK_URL=http://my-agent:8001

      # Service Configuration
      - PORT=8001
      - HOST=0.0.0.0

      # Your agent-specific env vars
      - OPENAI_API_KEY=${OPENAI_API_KEY}

    ports:
      - "8001:8001"  # host:container - use unique host ports per agent
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    restart: unless-stopped

# DO NOT include networks block - Coolify manages this
```

### Critical Notes:

1. **DO NOT add a `networks:` block** - Coolify ignores it and it can cause deployment errors
2. **Container name must be simple** - Use `my-agent`, not `my-agent-${UUID}`
3. **AGENT_CALLBACK_URL must match container name** - This is how the control plane calls back to your agent

---

## Step 2: Port Configuration

### Understanding Ports

```
Container Internal Port: 8001  (what your app listens on)
Host Mapped Port: 8003         (external access, must be unique)
Proxy Target Port: 8001        (ALWAYS use internal port)
```

### Port Mapping Example

| Agent | Internal Port | Host Port | Callback URL |
|-------|---------------|-----------|--------------|
| website-analyzer | 8001 | 8001 | http://website-analyzer:8001 |
| social-media-planner | 8002 | 8002 | http://social-media-planner:8002 |
| sentiment-agent | 8001 | 8003 | http://sentiment-agent:8001 |

### Common Mistake

```yaml
# WRONG - host port in callback URL
AGENT_CALLBACK_URL=http://sentiment-agent:8003

# CORRECT - internal port in callback URL
AGENT_CALLBACK_URL=http://sentiment-agent:8001
```

---

## Step 3: Coolify Service Configuration

### 3.1 Enable Predefined Network

1. Go to your service in Coolify
2. Navigate to **Settings** or **Advanced**
3. Enable **"Connect to Predefined Network"**
4. Save and redeploy

This connects your container to the `coolify` network where `agentfield` (control plane) is accessible.

### 3.2 Configure Domain/Proxy

1. Go to **Domains** section
2. Set your domain: `my-agent.apps.nolimitz.io`
3. **CRITICAL: Set port to INTERNAL port** (e.g., `8001`), NOT the host-mapped port
4. Save

### 3.3 Verify Service Selection

For docker-compose deployments:
1. Ensure a service is selected for the domain
2. The service name should match your docker-compose service name

---

## Step 4: Environment Variables

### Required Variables

```bash
# Control plane connection
AGENTFIELD_CONTROL_PLANE_URL=http://agentfield:8080

# Callback URL - MUST use container name and INTERNAL port
AGENT_CALLBACK_URL=http://<container-name>:<internal-port>
```

### Optional Variables

```bash
# OpenAI/LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Observability
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=https://langfuse.example.com
```

---

## Step 5: Network Verification

After deployment, verify networking:

```bash
# 1. Check container is on coolify network
docker inspect <container-name> --format '{{json .NetworkSettings.Networks}}' | jq 'keys'
# Should include "coolify"

# 2. Test DNS resolution from container
docker exec <container-name> getent hosts agentfield
# Should return IP address

# 3. Test control plane connectivity
docker exec <container-name> curl -s http://agentfield:8080/health
# Should return JSON health response

# 4. Verify agent registration
curl -s http://localhost:8080/api/v1/nodes/<agent-id>
# Should show health_status: "active"
```

---

## Step 6: Proxy Verification

```bash
# Test external endpoint
curl -I https://my-agent.apps.nolimitz.io/health

# Expected: HTTP 200
# If HTTP 502: Wrong port configured (use internal port, not host port)
# If timeout: DNS or network issue
```

---

## Troubleshooting Checklist

### Agent Shows "Offline" Despite Sending Heartbeats

| Check | Command | Fix |
|-------|---------|-----|
| Callback URL resolvable | `docker exec agentfield-... getent hosts <agent-name>` | Update AGENT_CALLBACK_URL to match container DNS name |
| Control plane can reach agent | Check control plane logs for callback errors | Ensure both on `coolify` network |

### 502 Bad Gateway

| Check | Fix |
|-------|-----|
| Proxy port | Change to internal port (e.g., 8001), not host port (e.g., 8003) |
| Container health | Verify `docker ps` shows container as healthy |
| Network | Ensure proxy and container share a network |

### "Could not resolve host: agentfield"

| Check | Fix |
|-------|-----|
| Predefined network enabled | Enable "Connect to Predefined Network" in Coolify |
| Container on coolify network | `docker network connect coolify <container-name>` (temporary) |

### Deployment Fails: "no service selected"

| Check | Fix |
|-------|-----|
| Service selection | In Coolify domain settings, select which docker-compose service gets the domain |

### Deployment Fails: "port already allocated"

| Check | Fix |
|-------|-----|
| Port conflict | Use unique host port: `8003:8001` instead of `8001:8001` |

---

## Network Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │         coolify network             │
                                    │                                     │
┌──────────────┐                    │  ┌─────────────────────────────┐   │
│   Internet   │◄───────────────────┼──│      coolify-proxy          │   │
└──────────────┘                    │  │  (Caddy/Traefik)            │   │
                                    │  └──────────────┬──────────────┘   │
                                    │                 │                   │
                                    │     ┌───────────┼───────────┐      │
                                    │     ▼           ▼           ▼      │
                                    │  ┌──────┐   ┌──────┐   ┌──────┐   │
                                    │  │agent1│   │agent2│   │agent3│   │
                                    │  │:8001 │   │:8002 │   │:8001 │   │
                                    │  └──┬───┘   └──┬───┘   └──┬───┘   │
                                    │     │          │          │        │
                                    │     └──────────┼──────────┘        │
                                    │                ▼                   │
                                    │  ┌─────────────────────────────┐   │
                                    │  │    agentfield:8080          │   │
                                    │  │    (control plane)          │   │
                                    │  └─────────────────────────────┘   │
                                    │                                     │
                                    └─────────────────────────────────────┘

All agents communicate via internal ports on the coolify network.
External access goes through coolify-proxy.
```

---

## Example: Complete Agent Deployment

### 1. docker-compose.yml

```yaml
services:
  my-new-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: my-new-agent
    labels:
      - "coolify.managed=true"
      - "coolify.service.type=web"
      - "coolify.service.port=8001"
      - "coolify.service.healthcheck=/health"
    environment:
      - AGENTFIELD_CONTROL_PLANE_URL=http://agentfield:8080
      - AGENT_CALLBACK_URL=http://my-new-agent:8001
      - PORT=8001
      - HOST=0.0.0.0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8004:8001"  # Unique host port, internal 8001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    restart: unless-stopped
```

### 2. Coolify Settings

- [ ] Domain: `my-new-agent.apps.nolimitz.io`
- [ ] Port: `8001` (internal port)
- [ ] Connect to Predefined Network: **Enabled**
- [ ] Service Selected: `my-new-agent`

### 3. Post-Deployment Verification

```bash
# Verify network
docker inspect my-new-agent-... --format '{{json .NetworkSettings.Networks}}' | jq 'keys'
# Expected: ["coolify", "..."]

# Verify control plane connection
curl -s http://localhost:8080/api/v1/nodes/my-new-agent | jq '{health_status, lifecycle_status}'
# Expected: {"health_status": "active", "lifecycle_status": "ready"}

# Verify external access
curl -s https://my-new-agent.apps.nolimitz.io/health
# Expected: {"status": "healthy"}
```

---

## Current Agent Inventory

| Agent | Container Name | Internal Port | Host Port | Domain |
|-------|---------------|---------------|-----------|--------|
| Control Plane | agentfield | 8080 | 8080 | agentfield.apps.nolimitz.io |
| Website Analyzer | website-analyzer | 8001 | 8001 | website-analyzer.apps.nolimitz.io |
| Social Media Planner | social-media-planner | 8002 | 8002 | social-media-planner.apps.nolimitz.io |
| Sentiment Agent | sentiment-agent | 8001 | 8003 | sentiment-agent.apps.nolimitz.io |

---

---

## Coolify API Automation

Coolify provides a REST API for automating service creation and configuration.

### API Authentication

1. Go to Coolify dashboard → **Keys & Tokens** → **API tokens**
2. Create a new token
3. Use as Bearer token in requests

```bash
export COOLIFY_TOKEN="your-api-token"
export COOLIFY_URL="http://localhost:3000"  # or your Coolify URL
```

### Key API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List applications | GET | `/api/v1/applications` |
| Create application | POST | `/api/v1/applications` |
| Update application | PATCH | `/api/v1/applications/{uuid}` |
| Get app config | GET | `/api/v1/applications/{uuid}` |
| Set env vars | POST | `/api/v1/applications/{uuid}/envs` |
| Update env var | PATCH | `/api/v1/applications/{uuid}/envs` |
| Deploy | GET | `/api/v1/deploy?uuid={uuid}` |
| List services | GET | `/api/v1/services` |
| Create service | POST | `/api/v1/services` |

### Example: Create Agent Service via API

```bash
#!/bin/bash
# create-agent.sh - Automate agent deployment

COOLIFY_URL="${COOLIFY_URL:-http://localhost:3000}"
COOLIFY_TOKEN="${COOLIFY_TOKEN}"
PROJECT_UUID="your-project-uuid"
ENVIRONMENT_NAME="staging"

# 1. Create application from Docker Compose
curl -X POST "${COOLIFY_URL}/api/v1/applications" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "'${PROJECT_UUID}'",
    "environment_name": "'${ENVIRONMENT_NAME}'",
    "type": "dockercompose",
    "docker_compose_raw": "'"$(cat docker-compose.yml | jq -Rs .)"'",
    "name": "my-new-agent",
    "description": "AgentField Agent"
  }'

# Response contains the new application UUID
```

### Example: Set Environment Variables

```bash
APP_UUID="your-app-uuid"

# Add environment variable
curl -X POST "${COOLIFY_URL}/api/v1/applications/${APP_UUID}/envs" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "AGENTFIELD_CONTROL_PLANE_URL",
    "value": "http://agentfield:8080",
    "is_build_time": false
  }'

curl -X POST "${COOLIFY_URL}/api/v1/applications/${APP_UUID}/envs" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "AGENT_CALLBACK_URL",
    "value": "http://my-agent:8001",
    "is_build_time": false
  }'
```

### Example: Update Application Settings

```bash
# Update port and network settings
curl -X PATCH "${COOLIFY_URL}/api/v1/applications/${APP_UUID}" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "ports_mappings": ["8005:8001"],
    "connect_to_docker_network": true
  }'
```

### Example: Deploy Application

```bash
# Trigger deployment
curl -X GET "${COOLIFY_URL}/api/v1/deploy?uuid=${APP_UUID}" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}"

# Force rebuild
curl -X GET "${COOLIFY_URL}/api/v1/deploy?uuid=${APP_UUID}&force=true" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}"
```

### Example: Check Deployment Status

```bash
# List deployments for application
curl -X GET "${COOLIFY_URL}/api/v1/deployments/app/${APP_UUID}" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" | jq '.[-1]'
```

### Full Automation Script

```bash
#!/bin/bash
# deploy-agentfield-agent.sh
# Usage: ./deploy-agentfield-agent.sh <agent-name> <internal-port> <host-port>

set -e

AGENT_NAME="${1:-my-agent}"
INTERNAL_PORT="${2:-8001}"
HOST_PORT="${3:-8005}"

COOLIFY_URL="${COOLIFY_URL:-http://localhost:3000}"
COOLIFY_TOKEN="${COOLIFY_TOKEN:?Set COOLIFY_TOKEN}"
PROJECT_UUID="${PROJECT_UUID:?Set PROJECT_UUID}"

echo "Creating agent: ${AGENT_NAME}"
echo "Ports: ${HOST_PORT}:${INTERNAL_PORT}"

# Create docker-compose content
COMPOSE_CONTENT=$(cat <<EOF
services:
  ${AGENT_NAME}:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ${AGENT_NAME}
    environment:
      - AGENTFIELD_CONTROL_PLANE_URL=http://agentfield:8080
      - AGENT_CALLBACK_URL=http://${AGENT_NAME}:${INTERNAL_PORT}
      - PORT=${INTERNAL_PORT}
      - HOST=0.0.0.0
    ports:
      - "${HOST_PORT}:${INTERNAL_PORT}"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${INTERNAL_PORT}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    restart: unless-stopped
EOF
)

# Create application
RESPONSE=$(curl -s -X POST "${COOLIFY_URL}/api/v1/applications" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "'${PROJECT_UUID}'",
    "environment_name": "staging",
    "type": "dockercompose",
    "docker_compose_raw": '"$(echo "$COMPOSE_CONTENT" | jq -Rs .)"',
    "name": "'${AGENT_NAME}'",
    "connect_to_docker_network": true
  }')

APP_UUID=$(echo "$RESPONSE" | jq -r '.uuid')
echo "Created application: ${APP_UUID}"

# Configure domain
curl -s -X PATCH "${COOLIFY_URL}/api/v1/applications/${APP_UUID}" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "fqdn": "https://'${AGENT_NAME}'.apps.nolimitz.io",
    "ports_exposes": "'${INTERNAL_PORT}'"
  }'

echo "Configured domain: ${AGENT_NAME}.apps.nolimitz.io"

# Deploy
curl -s -X GET "${COOLIFY_URL}/api/v1/deploy?uuid=${APP_UUID}" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}"

echo "Deployment triggered!"
echo ""
echo "Verify with:"
echo "  docker ps | grep ${AGENT_NAME}"
echo "  curl https://${AGENT_NAME}.apps.nolimitz.io/health"
```

### API Reference Links

- [Coolify API Docs](https://coolify.io/docs/api-reference/api/operations/deploy-by-tag-or-uuid)
- [Applications API](https://coolify.io/docs/applications/)
- [Services API](https://coolify.io/docs/services/introduction)

---

## Version History

| Date | Change |
|------|--------|
| 2026-01-25 | Initial guide created from deployment debugging session |
| 2026-01-25 | Added Coolify API automation section |
