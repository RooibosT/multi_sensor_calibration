#!/usr/bin/env python
import rospy
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2, PointField

from lgit_calibration_preprocessing.radar_target import select_target


class RadarPointCloudToPatternNode:
    def __init__(self):
        self.output_frame = rospy.get_param("~output_frame", "front_center_right_sonar_link")
        self.min_x = rospy.get_param("~min_x", 6.0)
        self.max_x = rospy.get_param("~max_x", 10.0)
        self.max_abs_y = rospy.get_param("~max_abs_y", 2.0)
        self.min_z = _optional_param("~min_z")
        self.max_z = _optional_param("~max_z")
        self.min_intensity = _optional_param("~min_intensity")
        self.selection = rospy.get_param("~selection", "max_intensity")
        self.pub = rospy.Publisher("~output", PointCloud2, queue_size=10)
        self.sub = rospy.Subscriber("~input", PointCloud2, self.callback, queue_size=10)

    def callback(self, msg):
        points = [
            {"x": point[0], "y": point[1], "z": point[2], "intensity": point[3]}
            for point in point_cloud2.read_points(
                msg,
                field_names=("x", "y", "z", "intensity"),
                skip_nans=True,
            )
        ]
        target = select_target(
            points,
            min_x=self.min_x,
            max_x=self.max_x,
            max_abs_y=self.max_abs_y,
            min_z=self.min_z,
            max_z=self.max_z,
            min_intensity=self.min_intensity,
            selection=self.selection,
        )
        if target is None:
            rospy.logwarn_throttle(2.0, "No radar reflector candidate in ROI.")
            return

        header = msg.header
        header.frame_id = self.output_frame
        fields = [
            PointField("x", 0, PointField.FLOAT32, 1),
            PointField("y", 4, PointField.FLOAT32, 1),
            PointField("z", 8, PointField.FLOAT32, 1),
        ]
        out = point_cloud2.create_cloud(
            header,
            fields,
            [(target["x"], target["y"], target["z"])],
        )
        self.pub.publish(out)


def _optional_param(name):
    return rospy.get_param(name) if rospy.has_param(name) else None


if __name__ == "__main__":
    rospy.init_node("radar_pc2_to_pattern")
    RadarPointCloudToPatternNode()
    rospy.spin()
