import math


def select_target(
    points,
    min_x=6.0,
    max_x=10.0,
    max_abs_y=2.0,
    min_z=None,
    max_z=None,
    min_intensity=None,
    selection="max_intensity",
):
    candidates = [
        point for point in points
        if _passes_roi(point, min_x, max_x, max_abs_y, min_z, max_z, min_intensity)
    ]
    if not candidates:
        return None

    if selection == "max_intensity":
        return max(candidates, key=lambda point: point["intensity"])
    if selection == "min_range":
        return min(candidates, key=_range_xy)
    if selection == "max_range":
        return max(candidates, key=_range_xy)

    raise ValueError("selection must be max_intensity, min_range, or max_range")


def _passes_roi(point, min_x, max_x, max_abs_y, min_z, max_z, min_intensity):
    for key in ("x", "y", "z", "intensity"):
        if not _is_finite(point[key]):
            return False
    if point["x"] < min_x or point["x"] > max_x:
        return False
    if abs(point["y"]) > max_abs_y:
        return False
    if min_z is not None and point["z"] < min_z:
        return False
    if max_z is not None and point["z"] > max_z:
        return False
    if min_intensity is not None and point["intensity"] < min_intensity:
        return False
    return True


def _range_xy(point):
    return math.hypot(point["x"], point["y"])


def _is_finite(value):
    return not (math.isnan(value) or math.isinf(value))
