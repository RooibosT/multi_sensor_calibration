# LGIT Calibration Quick Start

This guide runs the LGIT camera, Hesai AT128 LiDAR, and Continental radar calibration flow in the ROS1 Docker environment.

## 1. Start Docker With RViz Support

On the host:

```bash
cd /home/chan/Project/lgit/multi_sensor_calibration
./docker/ros1/run_docker.sh
```

The run script defaults to:

- data: `/media/chan/LGIT_chan/Dataset/LG_Innotek/CustomDataset/20260506`
- output: `<repo>/output`

It also runs `xhost +local:docker` when X11 is available.

Override paths only when needed:

```bash
DATA_DIR=/path/to/dataset OUTPUT_DIR=/path/to/output \
./docker/ros1/run_docker.sh
```

## 2. Build Workspace

Inside the container:

```bash
cd /workspace/calib_ws
catkin_make
source devel/setup.bash
```

## 3. Convert ROS2 Bag To ROS1 Bag

```bash
rosrun lgit_calibration_preprocessing convert_lgit_ros2_to_ros1_bag.py \
  /workspace/data/rosbag2_2026_05_06-14_09_26 \
  /workspace/data/rosbag1_2026_05_06-14_09_26.bag

rosbag info /workspace/data/rosbag1_2026_05_06-14_09_26.bag
```

Expected topics:

- `/camera0/image_raw`
- `/lidar_points`
- `/radar_detection_raw_conti`

## 4. Check LiDAR Ring Ordering

```bash
rosrun lgit_calibration_preprocessing analyze_lidar_order.py \
  /workspace/data/rosbag1_2026_05_06-14_09_26.bag \
  --topic /lidar_points \
  --layers 128
```

Use the recommended mode in the launch command. If unsure, start with `auto`.

## 5. Launch Calibration Pipeline

Terminal 1:

```bash
source /workspace/calib_ws/devel/setup.bash
roslaunch multi_sensor_calibration_launch lgit_three_sensor_calibration.launch ring_mode:=auto
```

This starts:

- Hesai AT128 ring converter
- radar reflector selector
- camera info publisher
- image rectification
- mono, lidar, accumulator, and optimizer nodes

## 6. Play Bag

Terminal 2:

```bash
source /workspace/calib_ws/devel/setup.bash
rosbag play /workspace/data/rosbag1_2026_05_06-14_09_26.bag --clock --pause -r 0.2
```

Press space in the `rosbag play` terminal to pause/resume.

## 7. Verify Pattern Topics

Terminal 3:

```bash
source /workspace/calib_ws/devel/setup.bash

rostopic echo -n 1 /lidar_detector/lidar_pattern/width
rostopic echo -n 1 /mono_detector/mono_pattern/width
rostopic echo -n 1 /radar_detector/radar_pattern/width
```

Expected:

- LiDAR width: `4`
- Mono camera width: `4`
- Radar width: `1`

Some LiDAR frames may publish width `0-3`; accumulate only during windows where width `4` appears reliably.

## 8. Open RViz

Terminal 4:

```bash
source /workspace/calib_ws/devel/setup.bash
rviz
```

Useful displays:

- `/velodyne_points`
- `/lidar_detector/lidar_pattern`
- `/mono_detector/mono_pattern`
- `/radar_detector/radar_pattern`
- `/accumulator/accumulated_patterns`

If RViz crashes with GLX errors, restart the container with `LIBGL_ALWAYS_SOFTWARE=1`.

## 9. Accumulate Board Poses

For each static board pose:

```bash
rosservice call /accumulator/toggle_accumulate
# wait 3-10 seconds while the board is static
rosservice call /accumulator/toggle_accumulate
```

Repeat for at least 10 board poses.

Save intermediate data:

```bash
rosservice call /accumulator/save "data: {data: '/workspace/output/lgit_accumulated.yaml'}"
```

Run optimization:

```bash
rosservice call /accumulator/optimize
```

## 10. Tune If Needed

- LiDAR ROI: `lidar_detector/config/config_lgit_at128.yaml`
- Camera Hough/ROI: `mono_detector/config/image_processing_lgit_6_10m.yaml`
- Radar ROI: `multi_sensor_calibration_launch/launch/lgit_three_sensor_calibration.launch`
