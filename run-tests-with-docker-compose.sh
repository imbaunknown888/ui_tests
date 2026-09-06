#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/infra/docker-compose/docker-compose.yaml"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-nbank-test-env}"
TEST_IMAGE="${TEST_IMAGE:-nbank-tests:latest}"

APIBASEURL="${APIBASEURL:-http://localhost:4111}"
UIBASEURL="${UIBASEURL:-http://localhost:3000}"

CONTAINER_API_BASE_URL="${CONTAINER_API_BASE_URL:-http://backend:4111}"
CONTAINER_UI_BASE_URL="${CONTAINER_UI_BASE_URL:-http://frontend:3000}"
CONTAINER_DB_HOST="${CONTAINER_DB_HOST:-postgres}"
CONTAINER_DB_PORT="${CONTAINER_DB_PORT:-5432}"

log() {
  printf '[run-tests] %s\n' "$*"
}

wait_for_service() {
  local service="$1"
  local timeout_seconds="${2:-120}"
  local started_at
  local container_id
  local status

  started_at="$(date +%s)"
  log "Waiting for ${service} to be ready..."

  while true; do
    container_id="$(
      docker compose \
        --project-name "${COMPOSE_PROJECT_NAME}" \
        -f "${COMPOSE_FILE}" \
        ps -q "${service}"
    )"

    if [[ -n "${container_id}" ]]; then
      status="$(
        docker inspect \
          --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
          "${container_id}"
      )"

      if [[ "${status}" == "healthy" || "${status}" == "running" ]]; then
        log "${service} is ready."
        return 0
      fi
    fi

    if (( "$(date +%s)" - started_at >= timeout_seconds )); then
      log "${service} was not ready after ${timeout_seconds} seconds."
      docker compose \
        --project-name "${COMPOSE_PROJECT_NAME}" \
        -f "${COMPOSE_FILE}" \
        ps
      return 1
    fi

    sleep 2
  done
}

cleanup() {
  local exit_code=$?
  log "Stopping test environment..."
  docker compose \
    --project-name "${COMPOSE_PROJECT_NAME}" \
    -f "${COMPOSE_FILE}" \
    down --remove-orphans
  exit "${exit_code}"
}

trap cleanup EXIT

log "Starting test environment with Docker Compose..."
docker compose \
  --project-name "${COMPOSE_PROJECT_NAME}" \
  -f "${COMPOSE_FILE}" \
  up -d

wait_for_service postgres 120
wait_for_service backend 180
wait_for_service frontend 120

log "Building tests image ${TEST_IMAGE}..."
docker build -t "${TEST_IMAGE}" "${SCRIPT_DIR}"

log "Running API and UI tests in a disposable container..."
docker run --rm \
  --network "${COMPOSE_PROJECT_NAME}_nbank-network" \
  -e APIBASEURL="${APIBASEURL}" \
  -e UIBASEURL="${UIBASEURL}" \
  -e server="${CONTAINER_API_BASE_URL}" \
  -e apiVersion="/api/v1" \
  -e UI_BASE_URL="${CONTAINER_UI_BASE_URL}" \
  -e PLAYWRIGHT_TEST_BASE_URL="${CONTAINER_UI_BASE_URL}" \
  -e DB_HOST="${CONTAINER_DB_HOST}" \
  -e DB_PORT="${CONTAINER_DB_PORT}" \
  -e DB_NAME="nbank" \
  -e DB_USERNAME="postgres" \
  -e DB_PASSWORD="postgres" \
  "${TEST_IMAGE}" \
  pytest -m "api or ui"

log "Tests finished successfully."
