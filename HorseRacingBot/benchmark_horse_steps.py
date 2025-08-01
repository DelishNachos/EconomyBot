import json
import random
import uuid

from utils import db, horse_generator
from utils.track_generator import get_current_track_point

AVG_STEPS = 140.5
AVG_PRICE = 500


def generate_random_horse(min_total=130, max_total=170):
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

    return {
        "id": str(uuid.uuid4()),
        "speed": stats[0],
        "stamina": stats[1],
        "agility": stats[2],
    }

def benchmark_average_steps(num_trials=500, horses_per_race=1, track_data=None, corner_indices=None, track_length=100):
    step_counts = []
    for _ in range(num_trials):
        horses = [horse_generator.generate_biased_horse() for _ in range(horses_per_race)]
        positions = {h["id"]: 0 for h in horses}
        steps = 0
        while max(positions.values()) < track_length:
            for horse in horses:
                horse_id = horse["id"]
                progress = positions[horse_id]
                percentage_progress = progress / track_length

                path_index = get_current_track_point([tuple(p) for p in track_data[0]], percentage_progress)
                on_corner = path_index in corner_indices

                # Base weights
                speed_weight = 1.5
                stamina_weight = 1.2
                agility_weight = 3.0 if on_corner else 1.0

                norm_speed = horse["speed"] / 10
                norm_stamina = horse["stamina"] / 10
                norm_agility = horse["agility"] / 10

                fatigue_percent = progress / track_length
                fatigue_penalty = fatigue_percent * (1 - norm_stamina / 10)
                effective_speed = norm_speed * (1 - 0.3 * fatigue_penalty)

                chance = (
                    (effective_speed * speed_weight) +
                    (norm_stamina * stamina_weight) +
                    (norm_agility * agility_weight)
                ) / 30

                if random.random() < chance:
                    positions[horse_id] += 1
            steps += 1
        step_counts.append(steps)
    return sum(step_counts) / len(step_counts)

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
    print(f"Horse steps: {horse_steps}")
    performance_ratio = (benchmark_steps / horse_steps) ** 2
    return int(base_price * performance_ratio)

def main():
    print("running")
    track = db.get_oval_track()
    track_data = db.get_track_data(track)
    if isinstance(track_data[-1], dict):
        corner_indices = track_data[-1].get("corner_indices", [])
    else:
        corner_indices = []

    benchmark = benchmark_average_steps(num_trials=1000, horses_per_race=1, track_data=track_data, corner_indices=corner_indices, track_length=track['track_steps'])
    print(benchmark)
    # horse = horse_generator.generate_biased_horse()
    # print(f"speed: {horse['speed']}\nstamina: {horse['stamina']}\nagility: {horse['agility']}\n")
    # price = calculate_horse_price(horse, AVG_STEPS, AVG_PRICE, track_data, corner_indices, track['track_steps'])
    # print(f"Price: {price}")



if __name__== "__main__":
    main()