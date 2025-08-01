import math

def generate_oval_track(cx, cy, width, height, num_points=100):
    a = width / 2
    b = height / 2
    points = []
    for i in range(num_points):
        theta = (2 * math.pi * i) / num_points
        x = cx + a * math.cos(theta)
        y = cy + b * math.sin(theta)
        points.append((x, y))
    return points

def get_oval_position(progress: float, width: int, height: int, margin: int = 80):
    """
    Get (x, y) coordinates on an oval track based on progress (0.0 to 1.0).
    Oval is drawn clockwise.
    """
    a = (width - margin * 2) / 2   # Horizontal radius
    b = (height - margin * 2) / 2  # Vertical radius
    cx = width / 2
    cy = height / 2

    # progress from 0.0 to 1.0 becomes angle from 0 to 2π (clockwise)
    theta = 2 * math.pi * progress
    x = cx + a * math.cos(-theta)
    y = cy + b * math.sin(-theta)
    return int(x), int(y)

def get_horse_position(path_points, progress):
    """
    Gets the (x, y) position on the path for a given progress (0.0 to 1.0).
    Uses linear interpolation between points.
    """
    if progress >= 1.0:
        return path_points[-1]
    total_segments = len(path_points) - 1
    index_float = progress * total_segments
    index = int(index_float)
    t = index_float - index  # Fractional progress within the segment

    x1, y1 = path_points[index]
    x2, y2 = path_points[index + 1]

    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    return (x, y)

def get_current_track_point(path_points, progress):
    if progress >= 1.0:
        return path_points[-1]
    total_segments = len(path_points) - 1
    index_float = progress * total_segments
    index = int(index_float)
    return index

def scale_and_translate_path(points, canvas_size, padding=50):
    min_x, min_y, max_x, max_y = get_path_bounds(points)
    path_width = max_x - min_x
    path_height = max_y - min_y

    canvas_width, canvas_height = canvas_size

    # Compute scale to fit path within canvas (keeping aspect ratio)
    scale_x = (canvas_width - 2 * padding) / path_width
    scale_y = (canvas_height - 2 * padding) / path_height
    scale = min(scale_x, scale_y)

    # Translate and scale all points
    new_points = []
    for x, y in points:
        new_x = (x - min_x) * scale + padding
        new_y = (y - min_y) * scale + padding
        new_points.append((new_x, new_y))

    return new_points

def get_path_bounds(points):
    xs = [x for x, y in points]
    ys = [y for x, y in points]
    return min(xs), min(ys), max(xs), max(ys)