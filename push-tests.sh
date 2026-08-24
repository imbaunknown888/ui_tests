#!/usr/bin/env bash
set -euo pipefail

# Required:
#   DOCKERHUB_USERNAME - Docker Hub username
#   DOCKERHUB_TOKEN    - Docker Hub access token
#
# Optional:
#   LOCAL_IMAGE        - local image name or ID to publish (default: nbank-tests:latest)
#   IMAGE_NAME         - Docker Hub repository/image name (default: nbank-tests)
#   IMAGE_TAG          - Docker Hub image tag (default: latest)

: "${DOCKERHUB_USERNAME:?Set DOCKERHUB_USERNAME to your Docker Hub username}"
: "${DOCKERHUB_TOKEN:?Set DOCKERHUB_TOKEN to your Docker Hub access token}"

LOCAL_IMAGE="${LOCAL_IMAGE:-nbank-tests:latest}"
IMAGE_NAME="${IMAGE_NAME:-nbank-tests}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REMOTE_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

if ! docker image inspect "${LOCAL_IMAGE}" >/dev/null 2>&1; then
  echo "Local image '${LOCAL_IMAGE}' was not found. Build it first, for example:"
  echo "docker build -t ${LOCAL_IMAGE} ."
  exit 1
fi

echo "Logging in to Docker Hub as ${DOCKERHUB_USERNAME}..."
printf '%s\n' "${DOCKERHUB_TOKEN}" | docker login --username "${DOCKERHUB_USERNAME}" --password-stdin

echo "Tagging local image ${LOCAL_IMAGE} as ${REMOTE_IMAGE}..."
docker tag "${LOCAL_IMAGE}" "${REMOTE_IMAGE}"

echo "Pushing ${REMOTE_IMAGE} to Docker Hub..."
docker push "${REMOTE_IMAGE}"

echo "Done."
echo "Docker Hub repository: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/${IMAGE_NAME}"
echo "Pull command: docker pull ${REMOTE_IMAGE}"
