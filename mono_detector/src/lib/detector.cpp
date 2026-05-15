/*
  multi_sensor_calibration
  Copyright (C) 2019 Intelligent Vehicles, Delft University of Technology

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "detector.hpp"
#include "util.hpp"
#include "types.hpp"
#include <limits>
#include <stdexcept>

namespace mono_detector {
namespace {

std::vector<cv::Point2f> circleCenters(std::vector<cv::Vec3f> const & circles) {
	std::vector<cv::Point2f> out;
	for (auto const & circle : circles) {
		out.push_back(cv::Point2f(circle[0], circle[1]));
	}
	return out;
}

std::vector<cv::Point2f> orderedCenters(std::vector<cv::Vec3f> const & circles) {
	std::vector<cv::Point2f> centers = circleCenters(circles);
	cv::Point2f center = calculateCenter(centers);
	std::sort(centers.begin(), centers.end(), [center](cv::Point2f a, cv::Point2f b) {
		return std::atan2(a.y - center.y, a.x - center.x) < std::atan2(b.y - center.y, b.x - center.x);
	});
	return centers;
}

double mean(std::vector<double> const & values) {
	double sum = 0.0;
	for (double value : values) {
		sum += value;
	}
	return sum / values.size();
}

double variance(std::vector<double> const & values, double const value_mean) {
	double sum = 0.0;
	for (double value : values) {
		double const diff = value - value_mean;
		sum += diff * diff;
	}
	return sum / values.size();
}

double relativeVariance(std::vector<double> const & values) {
	double const value_mean = mean(values);
	if (value_mean <= 0.0) {
		return std::numeric_limits<double>::max();
	}
	return variance(values, value_mean) / (value_mean * value_mean);
}

double boardGeometryScore(std::vector<cv::Vec3f> const & circles) {
	std::vector<cv::Point2f> points = orderedCenters(circles);
	double const area = std::abs(cv::contourArea(points));
	if (area < 100.0 || !cv::isContourConvex(points)) {
		return std::numeric_limits<double>::max();
	}

	std::vector<double> sides = {
		cv::norm(points[0] - points[1]),
		cv::norm(points[1] - points[2]),
		cv::norm(points[2] - points[3]),
		cv::norm(points[3] - points[0]),
	};
	std::vector<double> diagonals = {
		cv::norm(points[0] - points[2]),
		cv::norm(points[1] - points[3]),
	};
	std::vector<double> radii = {
		circles[0][2],
		circles[1][2],
		circles[2][2],
		circles[3][2],
	};

	double const side_mean = mean(sides);
	double const diagonal_mean = mean(diagonals);
	if (side_mean <= 0.0 || diagonal_mean <= side_mean) {
		return std::numeric_limits<double>::max();
	}

	double const expected_square_diagonal_ratio = std::sqrt(2.0);
	double const diagonal_ratio_error = std::abs((diagonal_mean / side_mean) - expected_square_diagonal_ratio);
	double const diagonal_balance = std::abs(diagonals[0] - diagonals[1]) / diagonal_mean;

	return relativeVariance(sides) + relativeVariance(radii) + diagonal_balance + diagonal_ratio_error;
}

}

std::vector<cv::Vec3f> selectBoardCircles(std::vector<cv::Vec3f> circles) {
	if (circles.size() <= 4) {
		return circles;
	}

	std::vector<cv::Vec3f> best_circles;
	double best_score = std::numeric_limits<double>::max();
	for (std::size_t a = 0; a < circles.size() - 3; ++a) {
		for (std::size_t b = a + 1; b < circles.size() - 2; ++b) {
			for (std::size_t c = b + 1; c < circles.size() - 1; ++c) {
				for (std::size_t d = c + 1; d < circles.size(); ++d) {
					std::vector<cv::Vec3f> candidate = {circles[a], circles[b], circles[c], circles[d]};
					double const score = boardGeometryScore(candidate);
					if (score < best_score) {
						best_score = score;
						best_circles = candidate;
					}
				}
			}
		}
	}

	return best_circles;
}

void detectMono(
	cv::Mat const & image,
	Configuration const & configuration,
	std::vector<cv::Point2f> & centers,
	std::vector<float> & radi
) {
	// Continue with a deep copy to prevent modification of original data
	cv::Mat processed = image.clone();

	// Optionally blur the image
	if (configuration.pre_blur.apply) {
		processed = gaussianBlur(processed, configuration.pre_blur);
	}

	// Optionally do edge detection on the image
	if (configuration.edge_detection.apply) {
		cv::Mat canny_filtered; // source and destination cannot be the same in canny filter
		cv::Canny(processed, canny_filtered, configuration.edge_detection.min_threshold, configuration.edge_detection.max_threshold);
		processed = canny_filtered;
	}

	// Optionally blur the image (AGAIN?)
	if (configuration.post_blur.apply) {
		processed = gaussianBlur(processed, configuration.post_blur);
	}

	// Detect circles with hough (because that's available in opencv)
	std::vector<cv::Vec3f> circles;
	cv::HoughCircles(
		processed,
		circles,
		CV_HOUGH_GRADIENT,
		configuration.hough_config.dp,
		configuration.hough_config.min_dist,
		configuration.hough_config.param1,
		configuration.hough_config.param2,
		configuration.hough_config.min_radius,
		configuration.hough_config.max_radius
	);

	// ToDo: Filter the 4 best scoring circles

	// Filter out circles with it's center outside the roi
	circles.erase(std::remove_if(circles.begin(), circles.end(), [configuration](cv::Vec3f p){return !configuration.roi.contains(cv::Point(p[0], p[1]));}), circles.end());

	circles = selectBoardCircles(circles);

	// visualize final circles that will be used for pose estimation
	if (configuration.visualize) {
		visualize(image, circles, configuration.roi);
	}

	// Only continue if the number of circles is exactly 4
	if (circles.size() != 4) {
		throw std::runtime_error("Number of circles found: '" + std::to_string(circles.size()) + "', but should be exactly 4.");
	}

	// Convert to vector of cv point 2f
	centers = toCvPoint2fVector(circles);

	// Sort in order to match correspondences with object points
	cv::Point2f origin = calculateCenter(centers);
	std::sort(centers.begin(), centers.end(), [origin](cv::Point2f a, cv::Point2f b) {
		return std::atan((a.y - origin.y) / (a.x - origin.x)) > std::atan((b.y - origin.y) / (b.x - origin.x));
	});

	// Convert to radi (float)
	for (const auto & circle : circles) {
		radi.push_back(circle[2]);
	}
}


}
