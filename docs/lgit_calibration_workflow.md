# LGIT Three-Sensor Calibration Workflow

This workflow calibrates `camera_0`, `hesai_lidar`, and `front_center_right_sonar_link` with the existing detectors, accumulator, and optimizer.

## Inputs

- ROS2 sqlite3 bag or ROS1 bag converted from it.
- Topics:
  - `/camera0/image_raw`
  - `/lidar_points`
  - `/radar_detection_raw_conti`

## Launch

```bash
roslaunch multi_sensor_calibration_launch lgit_three_sensor_calibration.launch
```

The launch starts:

- `hesai_to_velodyne`: adds `ring` to AT128 point clouds and publishes `/velodyne_points`.
- `radar_pc2_to_pattern`: selects one radar reflector point and publishes `/radar_detector/radar_pattern`.
- `camera_info_publisher`: publishes `/camera0/camera_info` with the LGIT intrinsics.
- `image_proc`: rectifies `/camera0/image_raw`.
- `mono_detector`, `lidar_detector`, `accumulator`, and `optimizer`.

## Convert Bag In Docker

Inside the ROS1 Docker container:

```bash
rosrun lgit_calibration_preprocessing convert_lgit_ros2_to_ros1_bag.py \
  /workspace/data/rosbag2_2026_05_06-14_09_26 \
  /workspace/data/rosbag1_2026_05_06-14_09_26.bag
```

The converter keeps:

- `/camera0/image_raw`
- `/lidar_points`
- `/radar_detection_raw_conti`

Check the output:

```bash
rosbag info /workspace/data/rosbag1_2026_05_06-14_09_26.bag
```

## LiDAR Ring Check

For a converted ROS1 bag, inspect flattened point ordering:

```bash
rosrun lgit_calibration_preprocessing analyze_lidar_order.py /path/to/input.bag --topic /lidar_points --layers 128
```

If the recommended mode is stable, pass it explicitly:

```bash
roslaunch multi_sensor_calibration_launch lgit_three_sensor_calibration.launch ring_mode:=block
```

Supported `ring_mode` values are `auto`, `block`, and `modulo`.

## Radar ROI Tuning

The default reflector selection is:

- `x` in `[6.0, 10.0]`
- `abs(y) <= 2.0`
- select max `intensity`

If the reflector is not selected, tune these params in `multi_sensor_calibration_launch/launch/lgit_three_sensor_calibration.launch`.

## LiDAR ROI Tuning

The LGIT launch uses `lidar_detector/config/config_lgit_at128.yaml`.

The default AT128 ROI assumes:

- `x` is forward
- `y` is lateral
- board distance is roughly `3-12 m`
- board lateral position is within `+/-3 m`

If PCL prints empty-cloud segmentation warnings and `/lidar_detector/lidar_pattern` does not publish, tune `pass_through_filter` in that YAML first.

## Camera Circle Tuning

The LGIT launch uses `mono_detector/config/image_processing_lgit_6_10m.yaml`.

The default circle radius assumes:

- board circle radius is `0.075 m`
- board distance is roughly `6-10 m`
- camera focal length is roughly `926 px`
- expected image circle radius is roughly `7-12 px`

If `/mono_detector/mono_pattern` does not publish, tune `hough.param2`, `hough.min_radius`, `hough.max_radius`, and `roi` in that YAML.

## Accumulation

Replay the bag slowly or paused. For each static board pose:

```bash
rosservice call /accumulator/toggle_accumulate
# wait 3-10 seconds while the board is static
rosservice call /accumulator/toggle_accumulate
```

After collecting at least 10 board poses:

```bash
rosservice call /accumulator/save "data: {data: '/tmp/lgit_accumulated.yaml'}"
rosservice call /accumulator/optimize
```
