FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    ROS_DISTRO=melodic \
    CATKIN_WS=/workspace/calib_ws

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    && sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list' \
    && echo "Fetching ROS apt key..." \
    && curl -fsSL --retry 5 --retry-delay 5 --connect-timeout 20 --max-time 120 \
        https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc \
        -o /tmp/ros.asc \
    && apt-key add /tmp/ros.asc \
    && rm -f /tmp/ros.asc \
    && apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libatlas-base-dev \
    libatlas3-base \
    libeigen3-dev \
    libopencv-dev \
    libyaml-cpp-dev \
    python-catkin-tools \
    python-rosdep \
    python-rospkg \
    python-rosinstall \
    python-rosinstall-generator \
    python-wstool \
    python3-dev \
    python3-matplotlib \
    python3-numpy \
    python3-pip \
    python3-scipy \
    python3-setuptools \
    python3-sklearn \
    python3-yaml \
    ros-${ROS_DISTRO}-astuff-sensor-msgs \
    ros-${ROS_DISTRO}-camera-calibration-parsers \
    ros-${ROS_DISTRO}-cmake-modules \
    ros-${ROS_DISTRO}-cv-bridge \
    ros-${ROS_DISTRO}-desktop-full \
    ros-${ROS_DISTRO}-image-geometry \
    ros-${ROS_DISTRO}-kdl-parser \
    ros-${ROS_DISTRO}-pcl-ros \
    ros-${ROS_DISTRO}-ros-numpy \
    ros-${ROS_DISTRO}-stereo-msgs \
    ros-${ROS_DISTRO}-urdf \
    ros-${ROS_DISTRO}-visualization-msgs \
    && (rosdep init || true) \
    && rosdep update --rosdistro "${ROS_DISTRO}" \
    && python3 -m pip install --no-cache-dir --upgrade "pip<22" setuptools wheel \
    && python3 -m pip install --no-cache-dir \
    rospkg \
    "rmsd==1.5.1" \
    "tikzplotlib==0.9.8" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p "${CATKIN_WS}/src" /workspace/data /workspace/output

WORKDIR ${CATKIN_WS}

RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc \
    && echo "[ -f ${CATKIN_WS}/devel/setup.bash ] && source ${CATKIN_WS}/devel/setup.bash" >> /root/.bashrc \
    && echo 'alias cm="catkin_make"' >> /root/.bashrc \
    && echo 'alias cb="catkin build"' >> /root/.bashrc \
    && echo 'alias sd="source devel/setup.bash"' >> /root/.bashrc \
    && echo 'export PS1="\[\e[32m\]multi_sensor_calib:\[\e[36m\]\w\[\e[0m\]\$ "' >> /root/.bashrc

CMD ["/bin/bash"]
