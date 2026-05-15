#!/usr/bin/env python
import copy

import rospy
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2, PointField

from lgit_calibration_preprocessing.lidar_ring import assign_rings, pitch_degrees, resolve_auto_mode


class HesaiToVelodyneNode:
    def __init__(self):
        self.layers = rospy.get_param("~layers", 128)
        self.ring_mode = rospy.get_param("~ring_mode", "auto")
        self.output_frame = rospy.get_param("~output_frame", "")
        self.vertical_angles = rospy.get_param("~vertical_angles", [])
        self.resolved_ring_mode = None
        self.pub = rospy.Publisher("~output", PointCloud2, queue_size=5)
        self.sub = rospy.Subscriber("~input", PointCloud2, self.callback, queue_size=2)

    def callback(self, msg):
        if not self._has_required_fields(msg):
            return

        points = list(
            point_cloud2.read_points(
                msg,
                field_names=("x", "y", "z", "intensity"),
                skip_nans=False,
            )
        )
        pitches = [pitch_degrees(point[0], point[1], point[2]) for point in points]
        ring_mode = self._ring_mode(pitches)
        rings = assign_rings(
            point_count=len(points),
            layers=self.layers,
            mode=ring_mode,
            pitches=pitches,
            vertical_angles=self.vertical_angles,
        )

        header = copy.copy(msg.header)
        if self.output_frame:
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

    def _has_required_fields(self, msg):
        field_names = set(field.name for field in msg.fields)
        missing_fields = {"x", "y", "z", "intensity"} - field_names
        if missing_fields:
            rospy.logerr_throttle(
                5.0,
                "Cannot convert Hesai cloud because fields are missing: %s"
                % ", ".join(sorted(missing_fields)),
            )
            return False
        return True

    def _ring_mode(self, pitches):
        if self.vertical_angles:
            return self.ring_mode
        if self.ring_mode != "auto":
            return self.ring_mode
        if self.resolved_ring_mode is None:
            self.resolved_ring_mode = resolve_auto_mode(pitches, self.layers)
            rospy.loginfo("Resolved auto ring mode to '%s'.", self.resolved_ring_mode)
        return self.resolved_ring_mode


if __name__ == "__main__":
    rospy.init_node("hesai_to_velodyne")
    HesaiToVelodyneNode()
    rospy.spin()
