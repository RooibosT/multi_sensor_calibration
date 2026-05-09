#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-multi_sensor_calibration:ros1}"
DOCKER_BUILDKIT="${DOCKER_BUILDKIT:-0}"
DOCKER_CPUSET_CPUS="${DOCKER_CPUSET_CPUS:-0-5}"
DOCKER_MEMORY="${DOCKER_MEMORY:-12g}"
DOCKER_MEMORY_SWAP="${DOCKER_MEMORY_SWAP:-12g}"
DOCKER_BUILD_LOG="${DOCKER_BUILD_LOG:-${ROOT_DIR}/docker/ros1/build.log}"

mkdir -p "$(dirname "${DOCKER_BUILD_LOG}")"
exec > >(tee -a "${DOCKER_BUILD_LOG}") 2>&1

echo "Building ${IMAGE_NAME}"
echo "  LOG=${DOCKER_BUILD_LOG}"
echo "  DOCKER_BUILDKIT=${DOCKER_BUILDKIT}"
echo "  DOCKER_CPUSET_CPUS=${DOCKER_CPUSET_CPUS}"
echo "  DOCKER_MEMORY=${DOCKER_MEMORY}"
echo "  DOCKER_MEMORY_SWAP=${DOCKER_MEMORY_SWAP}"

DOCKER_BUILDKIT="${DOCKER_BUILDKIT}" docker build \
    --cpuset-cpus="${DOCKER_CPUSET_CPUS}" \
    --memory="${DOCKER_MEMORY}" \
    --memory-swap="${DOCKER_MEMORY_SWAP}" \
    ${DOCKER_BUILD_EXTRA_ARGS:-} \
    -f "${ROOT_DIR}/docker/ros1/Dockerfile" \
    -t "${IMAGE_NAME}" \
    "${ROOT_DIR}"
