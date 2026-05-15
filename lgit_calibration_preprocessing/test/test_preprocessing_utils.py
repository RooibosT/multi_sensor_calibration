import math
import unittest

from lgit_calibration_preprocessing.camera_info import camera_matrices
from lgit_calibration_preprocessing.lidar_ring import assign_rings, choose_ordering, resolve_auto_mode
from lgit_calibration_preprocessing.radar_target import select_target


class LidarRingTest(unittest.TestCase):
    def test_choose_ordering_detects_block_order(self):
        pitches = [-1.0, -1.0, 0.0, 0.0, 1.0, 1.0]

        self.assertEqual(choose_ordering(pitches, 3), "block")

    def test_choose_ordering_detects_modulo_order(self):
        pitches = [-1.0, 0.0, 1.0, -1.0, 0.0, 1.0]

        self.assertEqual(choose_ordering(pitches, 3), "modulo")

    def test_resolve_auto_mode_uses_detected_ordering(self):
        pitches = [-1.0, 0.0, 1.0, -1.0, 0.0, 1.0]

        self.assertEqual(resolve_auto_mode(pitches, 3), "modulo")

    def test_assign_rings_uses_block_order_when_requested(self):
        rings = assign_rings(point_count=6, layers=3, mode="block")

        self.assertEqual(rings, [0, 0, 1, 1, 2, 2])

    def test_assign_rings_uses_modulo_order_when_requested(self):
        rings = assign_rings(point_count=6, layers=3, mode="modulo")

        self.assertEqual(rings, [0, 1, 2, 0, 1, 2])


class RadarTargetTest(unittest.TestCase):
    def test_select_target_keeps_highest_intensity_inside_roi(self):
        points = [
            {"x": 5.0, "y": 0.0, "z": 0.0, "intensity": 100.0},
            {"x": 7.0, "y": 0.5, "z": 1.0, "intensity": 12.0},
            {"x": 8.0, "y": 0.2, "z": 1.1, "intensity": 16.0},
            {"x": 9.0, "y": 4.0, "z": 1.0, "intensity": 20.0},
        ]

        target = select_target(points, min_x=6.0, max_x=10.0, max_abs_y=2.0)

        self.assertEqual(target["x"], 8.0)
        self.assertEqual(target["intensity"], 16.0)

    def test_select_target_returns_none_when_no_candidate_matches(self):
        points = [{"x": 3.0, "y": 0.0, "z": 0.0, "intensity": 100.0}]

        self.assertIsNone(select_target(points, min_x=6.0, max_x=10.0, max_abs_y=2.0))


class CameraInfoTest(unittest.TestCase):
    def test_camera_matrices_use_intrinsics_and_rational_distortion(self):
        matrices = camera_matrices(
            fx=926.4623,
            fy=926.33685,
            cx=960.8434,
            cy=538.19025,
            distortion=[
                8.4310e-01,
                1.4190e-01,
                -1.3000e-05,
                2.7200e-05,
                3.0000e-03,
                1.1989e00,
                3.4290e-01,
                2.1100e-02,
            ],
        )

        self.assertEqual(matrices["distortion_model"], "rational_polynomial")
        self.assertEqual(matrices["k"], [926.4623, 0.0, 960.8434, 0.0, 926.33685, 538.19025, 0.0, 0.0, 1.0])
        self.assertEqual(matrices["p"], [926.4623, 0.0, 960.8434, 0.0, 0.0, 926.33685, 538.19025, 0.0, 0.0, 0.0, 1.0, 0.0])
        self.assertTrue(math.isclose(matrices["d"][0], 0.84310))


if __name__ == "__main__":
    unittest.main()
