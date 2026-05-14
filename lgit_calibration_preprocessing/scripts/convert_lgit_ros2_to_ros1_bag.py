#!/usr/bin/env python
import argparse
import os
import sqlite3
import struct

import genpy
import rosbag
from sensor_msgs.msg import Image, PointCloud2, PointField


SUPPORTED_TYPES = {
    "sensor_msgs/msg/Image": "image",
    "sensor_msgs/msg/PointCloud2": "pointcloud2",
}


class CdrReader(object):
    def __init__(self, data):
        self.data = data
        self.offset = 4

    def align(self, size):
        remainder = self.offset % size
        if remainder:
            self.offset += size - remainder

    def uint8(self):
        self.align(1)
        value = struct.unpack_from("<B", self.data, self.offset)[0]
        self.offset += 1
        return value

    def bool(self):
        return bool(self.uint8())

    def int32(self):
        self.align(4)
        value = struct.unpack_from("<i", self.data, self.offset)[0]
        self.offset += 4
        return value

    def uint32(self):
        self.align(4)
        value = struct.unpack_from("<I", self.data, self.offset)[0]
        self.offset += 4
        return value

    def string(self):
        self.align(4)
        length = self.uint32()
        raw = self.data[self.offset:self.offset + length]
        self.offset += length
        if raw.endswith(b"\0"):
            raw = raw[:-1]
        return raw.decode("utf-8")

    def uint8_array_bytes(self):
        self.align(4)
        length = self.uint32()
        raw = self.data[self.offset:self.offset + length]
        self.offset += length
        return raw


def parse_header(reader):
    seconds = reader.int32()
    nanoseconds = reader.uint32()
    frame_id = reader.string()
    return genpy.Time(seconds, nanoseconds), frame_id


def parse_image(data):
    reader = CdrReader(data)
    msg = Image()
    msg.header.stamp, msg.header.frame_id = parse_header(reader)
    msg.height = reader.uint32()
    msg.width = reader.uint32()
    msg.encoding = reader.string()
    msg.is_bigendian = reader.uint8()
    msg.step = reader.uint32()
    msg.data = reader.uint8_array_bytes()
    return msg


def parse_pointcloud2(data):
    reader = CdrReader(data)
    msg = PointCloud2()
    msg.header.stamp, msg.header.frame_id = parse_header(reader)
    msg.height = reader.uint32()
    msg.width = reader.uint32()

    field_count = reader.uint32()
    msg.fields = []
    for _ in range(field_count):
        field = PointField()
        field.name = reader.string()
        field.offset = reader.uint32()
        field.datatype = reader.uint8()
        field.count = reader.uint32()
        msg.fields.append(field)

    msg.is_bigendian = reader.bool()
    msg.point_step = reader.uint32()
    msg.row_step = reader.uint32()
    msg.data = reader.uint8_array_bytes()
    msg.is_dense = reader.bool()
    return msg


def find_db3(input_dir):
    db3_files = [
        os.path.join(input_dir, name)
        for name in os.listdir(input_dir)
        if name.endswith(".db3")
    ]
    if len(db3_files) != 1:
        raise RuntimeError("Expected exactly one .db3 file in %s, found %d" % (input_dir, len(db3_files)))
    return db3_files[0]


def load_topics(cursor, selected_topics):
    topics = {}
    for topic_id, name, msg_type in cursor.execute("select id, name, type from topics"):
        if selected_topics and name not in selected_topics:
            continue
        if msg_type not in SUPPORTED_TYPES:
            continue
        topics[topic_id] = (name, msg_type)
    return topics


def parse_message(msg_type, data):
    kind = SUPPORTED_TYPES[msg_type]
    if kind == "image":
        return parse_image(data)
    if kind == "pointcloud2":
        return parse_pointcloud2(data)
    raise RuntimeError("Unsupported type %s" % msg_type)


def convert(input_dir, output_bag, selected_topics):
    db3_path = find_db3(input_dir)
    connection = sqlite3.connect(db3_path)
    cursor = connection.cursor()
    topics = load_topics(cursor, selected_topics)
    if not topics:
        raise RuntimeError("No supported topics found in %s" % db3_path)

    query = "select topic_id, timestamp, data from messages order by timestamp"
    written = {}
    with rosbag.Bag(output_bag, "w") as bag:
        for topic_id, timestamp, data in cursor.execute(query):
            if topic_id not in topics:
                continue
            topic_name, msg_type = topics[topic_id]
            msg = parse_message(msg_type, bytes(data))
            bag.write(topic_name, msg, genpy.Time(timestamp // 1000000000, timestamp % 1000000000))
            written[topic_name] = written.get(topic_name, 0) + 1
    return written


def main():
    parser = argparse.ArgumentParser(description="Convert LGIT ROS2 sqlite3 bag topics to a ROS1 bag inside the ROS1 Docker image.")
    parser.add_argument("input_dir", help="ROS2 bag directory containing metadata.yaml and one .db3 file")
    parser.add_argument("output_bag", help="Output ROS1 .bag path")
    parser.add_argument(
        "--topic",
        action="append",
        default=[],
        help="Topic to include. Repeatable. Defaults to camera0/lidar/radar LGIT topics.",
    )
    args = parser.parse_args()

    selected = args.topic or ["/camera0/image_raw", "/lidar_points", "/radar_detection_raw_conti"]
    written = convert(args.input_dir, args.output_bag, set(selected))
    for topic_name in sorted(written):
        print("%s: %d messages" % (topic_name, written[topic_name]))


if __name__ == "__main__":
    main()
