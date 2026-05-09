#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

IMAGE_NAME="${IMAGE_NAME:-multi_sensor_calibration:ros1}"
CONTAINER_NAME="${CONTAINER_NAME:-multi_sensor_calibration_ros1}"
CATKIN_WS="${CATKIN_WS:-/workspace/calib_ws}"
DATA_DIR="${DATA_DIR:-${ROOT_DIR}/data}"
OUTPUT_DIR="${OUTPUT_DIR:-${ROOT_DIR}/output}"

mkdir -p "${DATA_DIR}" "${OUTPUT_DIR}"

docker run -it --rm \
    --name "${CONTAINER_NAME}" \
    --net=host \
    --ipc=host \
    --pid=host \
    --shm-size "${SHM_SIZE:-8G}" \
    -e DISPLAY="${DISPLAY:-}" \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "${ROOT_DIR}:${CATKIN_WS}/src/multi_sensor_calibration" \
    -v "${DATA_DIR}:/workspace/data" \
    -v "${OUTPUT_DIR}:/workspace/output" \
    -w "${CATKIN_WS}" \
    ${DOCKER_EXTRA_ARGS:-} \
    "${IMAGE_NAME}" \
    "$@"
