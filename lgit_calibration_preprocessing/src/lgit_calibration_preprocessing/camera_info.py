def camera_matrices(fx, fy, cx, cy, distortion):
    return {
        "distortion_model": "rational_polynomial" if len(distortion) == 8 else "plumb_bob",
        "d": list(distortion),
        "k": [
            fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0,
        ],
        "r": [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ],
        "p": [
            fx, 0.0, cx, 0.0,
            0.0, fy, cy, 0.0,
            0.0, 0.0, 1.0, 0.0,
        ],
    }
