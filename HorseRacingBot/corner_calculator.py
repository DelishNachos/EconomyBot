import json
import math

def angle_between(p1, p2, p3):
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    mag1 = math.hypot(*v1)
    mag2 = math.hypot(*v2)
    if mag1 == 0 or mag2 == 0:
        return 180
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    cos_theta = max(min(dot / (mag1 * mag2), 1), -1)
    return math.degrees(math.acos(cos_theta))

def get_corner_zones(path, angle_threshold=10, zone_radius=3):
    corner_indices = []

    for i in range(1, len(path) - 1):
        angle = angle_between(path[i - 1], path[i], path[i + 1])
        if angle < (180 - angle_threshold):
            corner_indices.append(i)

    # Expand to corner zones
    corner_zone = set()
    for idx in corner_indices:
        for offset in range(-zone_radius, zone_radius + 1):
            if 0 <= idx + offset < len(path):
                corner_zone.add(idx + offset)

    return sorted(list(corner_zone))

# Load track
with open("data/tracks/oval_horse_track.json", "r") as f:
    track_data = json.load(f)

track_path = [tuple(p) for p in track_data[0]]

corner_zone_indices = get_corner_zones(track_path)

# Save back to file
track_data.append({"corner_indices": corner_zone_indices})

with open("data/tracks/oval_horse_track.json", "w") as f:
    json.dump(track_data, f, indent=2)