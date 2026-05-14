#!/usr/bin/env python
import rospy
from sensor_msgs.msg import CameraInfo, Image

from lgit_calibration_preprocessing.camera_info import camera_matrices


class SyncedCameraInfoPublisher:
    def __init__(self):
        self.width = rospy.get_param("~width", 1920)
        self.height = rospy.get_param("~height", 1080)
        self.frame_id = rospy.get_param("~frame_id", "camera_0")
        fx = rospy.get_param("~fx", 926.4623)
        fy = rospy.get_param("~fy", 926.33685)
        cx = rospy.get_param("~cx", 960.8434)
        cy = rospy.get_param("~cy", 538.19025)
        distortion = rospy.get_param(
            "~distortion",
            [0.84310, 0.14190, -0.000013, 0.0000272, 0.00300, 1.1989, 0.34290, 0.02110],
        )
        self.matrices = camera_matrices(fx, fy, cx, cy, distortion)
        self.pub = rospy.Publisher("~camera_info", CameraInfo, queue_size=10)
        self.sub = rospy.Subscriber("~image", Image, self.callback, queue_size=10)

    def callback(self, image):
        msg = CameraInfo()
        msg.header = image.header
        msg.header.frame_id = self.frame_id
        msg.width = self.width
        msg.height = self.height
        msg.distortion_model = self.matrices["distortion_model"]
        msg.D = self.matrices["d"]
        msg.K = self.matrices["k"]
        msg.R = self.matrices["r"]
        msg.P = self.matrices["p"]
        self.pub.publish(msg)


if __name__ == "__main__":
    rospy.init_node("camera_info_publisher")
    SyncedCameraInfoPublisher()
    rospy.spin()
