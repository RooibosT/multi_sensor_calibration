#!/usr/bin/env python
import argparse
import math

from lgit_calibration_preprocessing.lidar_ring import choose_ordering, pitch_degrees


def main():
    parser = argparse.ArgumentParser(description="Inspect flattened Hesai PointCloud2 ordering in a ROS1 bag.")
    parser.add_argument("bag")
    parser.add_argument("--topic", default="/lidar_points")
    parser.add_argument("--layers", type=int, default=128)
    args = parser.parse_args()

    import rosbag
    from sensor_msgs import point_cloud2

    with rosbag.Bag(args.bag) as bag:
        for _, msg, _ in bag.read_messages(topics=[args.topic]):
            points = list(point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=False))
            pitches = [pitch_degrees(point[0], point[1], point[2]) for point in points]
            finite = [pitch for pitch in pitches if not (math.isnan(pitch) or math.isinf(pitch))]
            print("points:", len(points))
            print("finite pitches:", len(finite))
            print("pitch min/max:", min(finite), max(finite))
            print("recommended ring_mode:", choose_ordering(pitches, args.layers))
            print("points per layer if block:", len(points) / float(args.layers))
            return

    raise SystemExit("No messages found on %s" % args.topic)


if __name__ == "__main__":
    main()
