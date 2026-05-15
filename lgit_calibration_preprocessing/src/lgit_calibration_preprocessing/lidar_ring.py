import math


def pitch_degrees(x, y, z):
    xy = math.hypot(x, y)
    if xy == 0.0 and z == 0.0:
        return float("nan")
    return math.degrees(math.atan2(z, xy))


def choose_ordering(pitches, layers):
    block_score = _ordering_score(pitches, layers, "block")
    modulo_score = _ordering_score(pitches, layers, "modulo")
    return "block" if block_score <= modulo_score else "modulo"


def resolve_auto_mode(pitches, layers):
    return choose_ordering(pitches, layers)


def assign_rings(point_count, layers, mode="auto", pitches=None, vertical_angles=None):
    if point_count <= 0:
        return []
    if layers <= 0:
        raise ValueError("layers must be positive")

    if vertical_angles:
        if pitches is None:
            raise ValueError("pitches are required when vertical_angles are provided")
        return [_nearest_angle_index(pitch, vertical_angles) for pitch in pitches]

    if mode == "auto":
        if pitches is None:
            raise ValueError("pitches are required for auto ring assignment")
        mode = resolve_auto_mode(pitches, layers)

    if mode == "block":
        points_per_ring = max(1, int(math.ceil(float(point_count) / layers)))
        return [min(index // points_per_ring, layers - 1) for index in range(point_count)]
    if mode == "modulo":
        return [index % layers for index in range(point_count)]

    raise ValueError("ring assignment mode must be auto, block, modulo, or vertical_angles")


def _ordering_score(pitches, layers, mode):
    groups = [[] for _ in range(layers)]
    point_count = len(pitches)
    if point_count == 0:
        return float("inf")

    points_per_ring = max(1, int(math.ceil(float(point_count) / layers)))
    for index, pitch in enumerate(pitches):
        if not is_finite(pitch):
            continue
        if mode == "block":
            ring = min(index // points_per_ring, layers - 1)
        else:
            ring = index % layers
        groups[ring].append(pitch)

    variances = [_variance(group) for group in groups if len(group) > 1]
    if not variances:
        return float("inf")
    return sum(variances) / len(variances)


def _variance(values):
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def _nearest_angle_index(pitch, vertical_angles):
    if not is_finite(pitch):
        return 0
    return min(range(len(vertical_angles)), key=lambda index: abs(vertical_angles[index] - pitch))


def is_finite(value):
    return not (math.isnan(value) or math.isinf(value))
