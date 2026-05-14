#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

IMAGE_NAME="${IMAGE_NAME:-multi_sensor_calibration:ros1}"
CONTAINER_NAME="${CONTAINER_NAME:-multi_sensor_calibration_ros1}"
CATKIN_WS="${CATKIN_WS:-/workspace/calib_ws}"
DATA_DIR="${DATA_DIR:-/media/chan/LGIT_chan/Dataset/LG_Innotek/CustomDataset/20260506}"
OUTPUT_DIR="${OUTPUT_DIR:-${ROOT_DIR}/output}"

mkdir -p "${DATA_DIR}" "${OUTPUT_DIR}"

if [[ -n "${DISPLAY:-}" ]] && command -v xhost >/dev/null 2>&1; then
    xhost +local:docker >/dev/null
fi

docker run -it --rm \
    --name "${CONTAINER_NAME}" \
    --gpus all \
    --net=host \
    --ipc=host \
    --pid=host \
    --shm-size "${SHM_SIZE:-64G}" \
    --cpus="${DOCKER_CPUS:-$(nproc)}" \
    -e DISPLAY="unix${DISPLAY:-}" \
    -e NVIDIA_DRIVER_CAPABILITIES="${NVIDIA_DRIVER_CAPABILITIES:-all}" \
    -e NVIDIA_VISIBLE_DEVICES="${NVIDIA_VISIBLE_DEVICES:-all}" \
    -e DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/1000/bus}" \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "${ROOT_DIR}:${CATKIN_WS}/src/multi_sensor_calibration" \
    -v "${DATA_DIR}:/workspace/data" \
    -v "${OUTPUT_DIR}:/workspace/output" \
    -w "${CATKIN_WS}" \
    ${DOCKER_EXTRA_ARGS:-} \
    "${IMAGE_NAME}" \
    "$@"
