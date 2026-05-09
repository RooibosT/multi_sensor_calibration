# Docker Usage

이 문서는 `multi_sensor_calibration` 레포를 ROS1 Docker 환경에서 빌드하고 실행하는 방법을 정리합니다. Docker 환경은 `osrf/ros:melodic-desktop-full-bionic` 베이스 이미지, 즉 Ubuntu 18.04 + ROS Melodic 기준입니다.

## Files

Docker 관련 파일은 아래 위치에 있습니다.

```bash
docker/ros1/Dockerfile
docker/ros1/build_docker.sh
docker/ros1/run_docker.sh
```

참고: 원본 README에는 `libatlas-dev`와 `ros-<distro>-opencv3`가 적혀 있지만, 현재 Ubuntu 18.04 + ROS Melodic apt 저장소에서는 각각 `libatlas-base-dev`, `libopencv-dev`/ROS OpenCV 관련 패키지 조합으로 설치합니다. Dockerfile은 현재 설치 가능한 패키지명에 맞춰져 있고, ROS apt source/key 설정은 베이스 이미지에 맡깁니다.

Python 패키지는 재현성을 위해 버전을 고정합니다. `rmsd`는 PyPI에서 `1.5.1` 배포본이 없어 Dockerfile에서 `rmsd==1.5.0`을 사용합니다.

## Host Prerequisites

호스트 머신에는 Docker가 설치되어 있어야 합니다.

GUI 도구(RViz, matplotlib window 등)를 컨테이너에서 띄울 경우 X11 접근 권한이 필요합니다.

```bash
xhost +local:docker
```

작업이 끝난 뒤 권한을 되돌리려면:

```bash
xhost -local:docker
```

## Build Image

레포 루트에서 아래 명령을 실행합니다.

```bash
./docker/ros1/build_docker.sh
```

기본 이미지 이름은 `multi_sensor_calibration:ros1`입니다. 빌드 중 데스크탑 부하를 줄이기 위해 스크립트는 기본적으로 아래 제한을 적용합니다.

| Setting | Default |
| --- | --- |
| `DOCKER_BUILDKIT` | `0` |
| `DOCKER_CPUSET_CPUS` | `0-5` |
| `DOCKER_MEMORY` | `12g` |
| `DOCKER_MEMORY_SWAP` | `12g` |

다른 이름을 쓰고 싶으면 `IMAGE_NAME`을 지정합니다.

```bash
IMAGE_NAME=my_calib:melodic ./docker/ros1/build_docker.sh
```

CPU와 메모리 제한은 호스트 사양에 맞춰 조절할 수 있습니다.

```bash
DOCKER_CPUSET_CPUS=0-3 DOCKER_MEMORY=8g DOCKER_MEMORY_SWAP=8g ./docker/ros1/build_docker.sh
```

추가 Docker build 옵션이 필요하면 `DOCKER_BUILD_EXTRA_ARGS`를 사용합니다.

```bash
DOCKER_BUILD_EXTRA_ARGS="--no-cache" ./docker/ros1/build_docker.sh
```

빌드 출력은 터미널과 아래 로그 파일에 동시에 기록됩니다.

```bash
docker/ros1/build.log
```

다른 터미널에서 진행 상황을 확인하려면:

```bash
tail -f docker/ros1/build.log
```

로그 파일 경로를 바꾸려면 `DOCKER_BUILD_LOG`를 지정합니다.

```bash
DOCKER_BUILD_LOG=/tmp/multi_sensor_calibration_build.log ./docker/ros1/build_docker.sh
```

## Run Container

레포 루트에서 아래 명령을 실행합니다.

```bash
./docker/ros1/run_docker.sh
```

컨테이너가 시작되면 현재 레포는 다음 경로에 마운트됩니다.

```bash
/workspace/calib_ws/src/multi_sensor_calibration
```

기본 작업 디렉터리는 catkin workspace입니다.

```bash
/workspace/calib_ws
```

## Build Catkin Workspace

컨테이너 안에서 아래 명령을 실행합니다.

```bash
catkin_make
source devel/setup.bash
```

`~/.bashrc`에 ROS Melodic setup과 workspace setup이 등록되어 있으므로 새 shell에서는 보통 자동으로 source됩니다. 그래도 빌드 직후에는 `source devel/setup.bash`를 직접 실행하는 것이 안전합니다.

## Run Calibration Nodes

전체 예시 launch를 한 번에 실행하려면:

```bash
roslaunch multi_sensor_calibration_launch prius_extrinsic_calibration.launch
```

노드를 나눠서 실행하려면 터미널을 여러 개 열고 각각 실행합니다.

```bash
roscore
```

```bash
roslaunch multi_sensor_calibration_launch detectors.launch
```

```bash
roslaunch multi_sensor_calibration_launch accumulator.launch
```

```bash
roslaunch multi_sensor_calibration_launch optimizer.launch
```

보드 위치를 수집하고 최적화를 실행하는 기본 흐름은:

```bash
rosservice call /accumulator/toggle_accumulate
# Wait 5-10 seconds while detections are collected.
rosservice call /accumulator/toggle_accumulate

# Repeat for multiple board locations, then optimize.
rosservice call /accumulator/optimize
```

## Mounted Paths

`run_docker.sh`는 기본적으로 아래 경로를 마운트합니다.

| Host path | Container path | Purpose |
| --- | --- | --- |
| repo root | `/workspace/calib_ws/src/multi_sensor_calibration` | catkin source package |
| `./data` | `/workspace/data` | optional datasets, rosbags, inputs |
| `./output` | `/workspace/output` | optional generated outputs |
| `/tmp/.X11-unix` | `/tmp/.X11-unix` | X11 GUI forwarding |

`./data`와 `./output`은 없으면 실행 스크립트가 자동으로 생성합니다.

## Runtime Options

환경변수로 실행 설정을 바꿀 수 있습니다.

```bash
IMAGE_NAME=my_calib:melodic ./docker/ros1/run_docker.sh
```

```bash
DATA_DIR=/path/to/dataset OUTPUT_DIR=/path/to/output ./docker/ros1/run_docker.sh
```

```bash
SHM_SIZE=16G ./docker/ros1/run_docker.sh
```

추가 Docker 옵션이 필요하면 `DOCKER_EXTRA_ARGS`를 사용합니다.

```bash
DOCKER_EXTRA_ARGS="--privileged -v /dev:/dev" ./docker/ros1/run_docker.sh
```

특정 명령을 컨테이너 시작과 동시에 실행할 수도 있습니다.

```bash
./docker/ros1/run_docker.sh bash -lc "catkin_make && source devel/setup.bash"
```

## Sensor Topic Setup

기본 launch는 예제 토픽 이름을 사용합니다.

| Sensor | Default input topic |
| --- | --- |
| Lidar | `/velodyne_points` |
| Stereo camera | `/ueye/left/image_rect_color`, `/ueye/left/camera_info`, `/ueye/right/camera_info`, `/ueye/disparity` |
| Radar | `/radar_converter/detections` |

실제 장비 토픽이 다르면 launch 파일에서 remap을 추가하거나 detector node 실행 시 remap을 걸어야 합니다.

Accumulator는 기본적으로 detector output을 아래 토픽에서 수집합니다.

```bash
/stereo_detector/stereo_pattern
/lidar_detector/lidar_pattern
/radar_detector/radar_pattern
```

여러 센서 또는 mono camera를 사용할 경우 accumulator의 `~sensor_topics` 파라미터를 장비 구성에 맞게 바꿔야 합니다. topic 이름에는 `lidar`, `stereo`, `mono`, `radar` 중 해당 센서 타입 문자열이 들어가야 optimizer가 타입을 판별할 수 있습니다.

## Troubleshooting

GUI 창이 뜨지 않으면 호스트에서 X11 권한을 먼저 확인합니다.

```bash
xhost +local:docker
echo $DISPLAY
```

ROS 패키지를 찾지 못하면 컨테이너 안에서 workspace setup을 다시 source합니다.

```bash
source /opt/ros/melodic/setup.bash
source /workspace/calib_ws/devel/setup.bash
```

catkin 빌드가 dependency 오류로 실패하면 컨테이너 안에서 rosdep을 다시 실행합니다.

```bash
cd /workspace/calib_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make
```

장비 접근이 필요한 경우 `DOCKER_EXTRA_ARGS`로 device mount나 privileged 옵션을 추가합니다.

```bash
DOCKER_EXTRA_ARGS="--privileged -v /dev:/dev" ./docker/ros1/run_docker.sh
```
