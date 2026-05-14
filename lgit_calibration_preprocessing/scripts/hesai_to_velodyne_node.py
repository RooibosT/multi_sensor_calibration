#!/usr/bin/env python
import rospy
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2, PointField

from lgit_calibration_preprocessing.lidar_ring import assign_rings, pitch_degrees


class HesaiToVelodyneNode:
    def __init__(self):
        self.layers = rospy.get_param("~layers", 128)
        self.ring_mode = rospy.get_param("~ring_mode", "auto")
        self.output_frame = rospy.get_param("~output_frame", "hesai_lidar")
        self.vertical_angles = rospy.get_param("~vertical_angles", [])
        self.pub = rospy.Publisher("~output", PointCloud2, queue_size=5)
        self.sub = rospy.Subscriber("~input", PointCloud2, self.callback, queue_size=2)

    def callback(self, msg):
        points = list(point_cloud2.read_points(
            msg,
            field_names=("x", "y", "z", "intensity"),
            skip_nans=False,
        ))
        pitches = [pitch_degrees(point[0], point[1], point[2]) for point in points]
        rings = assign_rings(
            point_count=len(points),
            layers=self.layers,
            mode=self.ring_mode,
            pitches=pitches,
            vertical_angles=self.vertical_angles,
        )

        header = msg.header
        header.frame_id = self.output_frame
        fields = [
            PointField("x", 0, PointField.FLOAT32, 1),
            PointField("y", 4, PointField.FLOAT32, 1),
            PointField("z", 8, PointField.FLOAT32, 1),
            PointField("intensity", 12, PointField.FLOAT32, 1),
            PointField("ring", 16, PointField.UINT16, 1),
        ]
        out_points = [
            (point[0], point[1], point[2], point[3], int(ring))
            for point, ring in zip(points, rings)
        ]
        self.pub.publish(point_cloud2.create_cloud(header, fields, out_points))


if __name__ == "__main__":
    rospy.init_node("hesai_to_velodyne")
    HesaiToVelodyneNode()
    rospy.spin()
