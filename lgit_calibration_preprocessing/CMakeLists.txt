cmake_minimum_required(VERSION 2.8.3)
project(lgit_calibration_preprocessing)

find_package(catkin REQUIRED COMPONENTS
  rospy
  sensor_msgs
  std_msgs
)

catkin_python_setup()

catkin_package()

catkin_install_python(PROGRAMS
  scripts/analyze_lidar_order.py
  scripts/camera_info_publisher_node.py
  scripts/convert_lgit_ros2_to_ros1_bag.py
  scripts/hesai_to_velodyne_node.py
  scripts/radar_pc2_to_pattern_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

if(CATKIN_ENABLE_TESTING)
  catkin_add_nosetests(test)
endif()
