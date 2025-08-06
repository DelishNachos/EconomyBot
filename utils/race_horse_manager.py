import datetime
import json
import random
from pathlib import Path
from utils import db

MAX_ENERGY = 100

def load_horses():
    return db.load_all_horses()

def select_random_race_horses(count=3):
    return db.get_random_public_horses(count)

def total_stats(horse):
    return horse["speed"] + horse["stamina"] + horse["agility"]

def select_close_random_race_horses(count=3):
    all_horses = db.load_all_horses()

    # Filter out house horses
    user_horses = [h for h in all_horses if h["owner"] != "house"]
    if not user_horses:
        return []

    # Step 1: Pick a random user horse
    selected = [random.choice(user_horses)]
    selected_total = total_stats(selected[0])
    print(f"Horse 1: {selected_total}")

    # Step 2: Sort remaining horses by stat difference
    remaining = [h for h in all_horses if h["id"] != selected[0]["id"]]
    for _ in range(count - 1):
        # Sort by absolute stat difference
        sorted_by_diff = sorted(remaining, key=lambda h: abs(total_stats(h) - selected_total))
        
        # Get candidates within 20 points difference
        close_enough = [h for h in sorted_by_diff if abs(total_stats(h) - selected_total) <= db.get_general_config()['random_race_stat_difference']]

        if close_enough:
            next_horse = random.choice(close_enough)
        else:
            # No close match, use the closest one
            next_horse = sorted_by_diff[0]

        selected.append(next_horse)
        remaining = [h for h in remaining if h["id"] != next_horse["id"]]
        print(f"horse: {total_stats(next_horse)}")

    return selected

def get_horse_by_id(horse_id):
    return db.get_horse_by_id(horse_id)

def regenerate_energy(horse):
    ENERGY_REGEN_PER_HOUR = db.get_general_config()['energy_per_hour']
    now = datetime.datetime.now(datetime.timezone.utc)

    # If last_energy_update is None or missing, initialize it to now
    if not horse.get("last_energy_update"):
        horse["last_energy_update"] = now.isoformat()
        # Optionally you can also set energy to max here if you want to reset it
        horse["energy"] = horse.get("energy", MAX_ENERGY)
        db.update_horse(horse)
        return

    last_update = datetime.datetime.fromisoformat(horse["last_energy_update"])
    elapsed = now - last_update
    hours_passed = elapsed.total_seconds() / 3600
    regenerated = int(hours_passed * ENERGY_REGEN_PER_HOUR)

    if regenerated > 0:
        new_energy = min(horse["energy"] + regenerated, MAX_ENERGY)
        horse["energy"] = new_energy
        horse["last_energy_update"] = now.isoformat()
        db.update_horse(horse)