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