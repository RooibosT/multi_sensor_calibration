#include <gtest/gtest.h>

#include "accumulator.hpp"

TEST(PatternSizeFilter, AcceptsExpectedSensorPatternSizes) {
	EXPECT_TRUE(accumulator::hasExpectedPatternSize("/lidar_detector/lidar_pattern", 4, 1, 4));
	EXPECT_TRUE(accumulator::hasExpectedPatternSize("/mono_detector/mono_pattern", 4, 1, 4));
	EXPECT_TRUE(accumulator::hasExpectedPatternSize("/radar_detector/radar_pattern", 1, 1, 4));
}

TEST(PatternSizeFilter, RejectsUnexpectedSensorPatternSizes) {
	EXPECT_FALSE(accumulator::hasExpectedPatternSize("/lidar_detector/lidar_pattern", 3, 1, 4));
	EXPECT_FALSE(accumulator::hasExpectedPatternSize("/lidar_detector/lidar_pattern", 0, 1, 4));
	EXPECT_FALSE(accumulator::hasExpectedPatternSize("/mono_detector/mono_pattern", 3, 1, 4));
	EXPECT_FALSE(accumulator::hasExpectedPatternSize("/radar_detector/radar_pattern", 4, 1, 4));
}

TEST(PatternSizeFilter, LeavesUnknownTopicsUnfiltered) {
	EXPECT_TRUE(accumulator::hasExpectedPatternSize("/custom_detector/custom_pattern", 0, 1, 4));
	EXPECT_TRUE(accumulator::hasExpectedPatternSize("/custom_detector/custom_pattern", 7, 1, 4));
}
