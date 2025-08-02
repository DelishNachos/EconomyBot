import json
from pathlib import Path
import random
import uuid

from utils import db
from utils.track_generator import get_current_track_point


BOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BOT_DIR.parent / "HorseRacingBotData" / "Data"
TRACK_ID = "oval_horse_track"

CONFIG_PATH = DATA_PATH / "horse_racing_config.json"

def generate_biased_horse(caliber="H5", track_type="balanced"):
    AVG_PRICE = db.get_general_config()['average_horse_price']
    AVG_STEPS = db.get_general_config()['average_horse_steps']
    CALIBER_INFO = db.get_horse_racing_caliber_info()
    TRACK_BIASES = db.get_horse_racing_bias_settings()
    horse = db.empty_horse_table_item(str(uuid.uuid4()))

    # Step 1: Total stat allocation
    min_total, max_total = CALIBER_INFO[caliber]['points']
    min_energy, max_energy = CALIBER_INFO[caliber]['energy']
    total = random.randint(min_total, max_total)

    # Step 2: Get bias weights for the track type
    bias = TRACK_BIASES.get(track_type, TRACK_BIASES["balanced"])
    weights = [bias["speed"], bias["stamina"], bias["agility"]]
    weight_sum = sum(weights)
    weights = [w / weight_sum for w in weights]  # normalize weights

    # Step 2.5: Distribute points randomly using weights as bias tendencies
    raw = [random.gammavariate(w * 5, 1) for w in weights]
    raw_total = sum(raw)
    stats = [int(total * r / raw_total) for r in raw]

    # Clamp stats to 0–150
    for i in range(3):
        stats[i] = max(0, min(150, stats[i]))

    # Fix rounding error
    current_total = sum(stats)
    while current_total != total:
        diff = total - current_total
        i = random.randint(0, 2)
        if diff > 0 and stats[i] < 120:
            add = min(diff, 120 - stats[i])
            stats[i] += add
            current_total += add
        elif diff < 0 and stats[i] > 20:
            sub = min(-diff, stats[i] - 20)
            stats[i] -= sub
            current_total -= sub

    horse["speed"] = stats[0]
    horse["stamina"] = stats[1]
    horse["agility"] = stats[2]
    horse["energy"] = random.randint(min_energy, max_energy)

    # === Calculate price using benchmark track ===
    track = db.get_track_by_id(TRACK_ID)
    track_data = json.load(open(f'{DATA_PATH}/tracks/{TRACK_ID}.json'))
    if isinstance(track_data[-1], dict):
        corner_indices = track_data[-1].get("corner_indices", [])
    else:
        corner_indices = []

    price = calculate_horse_price(
        horse, AVG_STEPS, AVG_PRICE,
        track_data, corner_indices, track['track_steps']
    )
    horse['market_price'] = price

    return horse

def generate_random_horse(min_total=130, max_total=170):
    AVG_PRICE = db.get_general_config()['average_horse_price']
    AVG_STEPS = db.get_general_config()['average_horse_steps']
    
    total = random.randint(min_total, max_total)

    # Widened weight range allows much greater variation
    weights = [random.uniform(0.3, 1.7) for _ in range(3)]
    weight_sum = sum(weights)
    weights = [w / weight_sum for w in weights]

    stats = [int(total * w) for w in weights]

    # Clamp stats to between 20 and 120
    for i in range(3):
        stats[i] = max(20, min(120, stats[i]))

    # Fix any rounding/clamping error in total sum
    current_total = sum(stats)
    while current_total != total:
        diff = total - current_total
        i = random.randint(0, 2)

        if diff > 0 and stats[i] < 120:
            add = min(diff, 120 - stats[i])
            stats[i] += add
            current_total += add
        elif diff < 0 and stats[i] > 20:
            sub = min(-diff, stats[i] - 20)
            stats[i] -= sub
            current_total -= sub

    horse = db.empty_horse_table_item(str(uuid.uuid4()))
    horse["speed"] = stats[0]
    horse["stamina"] = stats[1]
    horse["agility"] = stats[2]

    # === Getting Price ===
    track = db.get_track_by_id(TRACK_ID)
    track_data = json.load(open(f'{DATA_PATH}/tracks/{TRACK_ID}.json'))
    if isinstance(track_data[-1], dict):
        corner_indices = track_data[-1].get("corner_indices", [])
    else:
        corner_indices = []

    price = calculate_horse_price(horse, AVG_STEPS, AVG_PRICE, track_data, corner_indices, track['track_steps'])
    horse['market_price'] = price

    return horse

def simulate_horse_steps(horse, num_runs, track_data, corner_indices, track_length):
    step_totals = []
    for _ in range(num_runs):
        position = 0
        steps = 0
        while position < track_length:
            percentage_progress = position / track_length
            path_index = get_current_track_point([tuple(p) for p in track_data[0]], percentage_progress)
            on_corner = path_index in corner_indices

            speed_weight = 1.5
            stamina_weight = 1.2
            agility_weight = 3.0 if on_corner else 1.0

            norm_speed = horse["speed"] / 10
            norm_stamina = horse["stamina"] / 10
            norm_agility = horse["agility"] / 10

            fatigue_percent = position / track_length
            fatigue_penalty = fatigue_percent * (1 - norm_stamina / 10)
            effective_speed = norm_speed * (1 - 0.3 * fatigue_penalty)

            chance = (
                (effective_speed * speed_weight) +
                (norm_stamina * stamina_weight) +
                (norm_agility * agility_weight)
            ) / 30

            if random.random() < chance:
                position += 1
            steps += 1
        step_totals.append(steps)
    return sum(step_totals) / len(step_totals)

def calculate_horse_price(horse, benchmark_steps, base_price, track_data, corner_indices, track_length):
    horse_steps = simulate_horse_steps(horse, num_runs=100, track_data=track_data, corner_indices=corner_indices, track_length=track_length)
    performance_ratio = (benchmark_steps / horse_steps) ** 2
    return int(base_price * performance_ratio)

def generate_daily_horses():
    return [generate_biased_horse() for _ in range(3)]