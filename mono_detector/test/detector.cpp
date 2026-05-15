#include <gtest/gtest.h>

#include "detector.hpp"

#include <algorithm>
#include <vector>

namespace {

std::vector<cv::Point2f> centers(std::vector<cv::Vec3f> const & circles) {
	std::vector<cv::Point2f> out;
	for (auto const & circle : circles) {
		out.push_back(cv::Point2f(circle[0], circle[1]));
	}
	std::sort(out.begin(), out.end(), [](cv::Point2f const & lhs, cv::Point2f const & rhs) {
		if (lhs.x == rhs.x) {
			return lhs.y < rhs.y;
		}
		return lhs.x < rhs.x;
	});
	return out;
}

bool containsNear(std::vector<cv::Point2f> const & points, cv::Point2f const & expected) {
	return std::any_of(points.begin(), points.end(), [expected](cv::Point2f const & point) {
		return cv::norm(point - expected) < 1.0;
	});
}

}

TEST(Detector, SelectBoardCirclesPrefersTwoByTwoGridOverDistractors) {
	std::vector<cv::Vec3f> circles = {
		cv::Vec3f(600, 420, 12),
		cv::Vec3f(690, 418, 12),
		cv::Vec3f(604, 510, 11),
		cv::Vec3f(694, 508, 12),
		cv::Vec3f(250, 200, 12),
		cv::Vec3f(1050, 300, 12),
		cv::Vec3f(980, 760, 12),
		cv::Vec3f(740, 440, 5),
	};

	std::vector<cv::Point2f> selected = centers(mono_detector::selectBoardCircles(circles));

	ASSERT_EQ(4u, selected.size());
	EXPECT_TRUE(containsNear(selected, cv::Point2f(600, 420)));
	EXPECT_TRUE(containsNear(selected, cv::Point2f(690, 418)));
	EXPECT_TRUE(containsNear(selected, cv::Point2f(604, 510)));
	EXPECT_TRUE(containsNear(selected, cv::Point2f(694, 508)));
}

TEST(Detector, SelectBoardCirclesReturnsInputWhenFourOrFewerCandidatesExist) {
	std::vector<cv::Vec3f> circles = {
		cv::Vec3f(600, 420, 12),
		cv::Vec3f(690, 418, 12),
		cv::Vec3f(604, 510, 11),
	};

	EXPECT_EQ(3u, mono_detector::selectBoardCircles(circles).size());
}
