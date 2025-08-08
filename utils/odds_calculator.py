import copy
from collections import Counter
import math
import random
from utils import db
from utils.track_generator import get_current_track_point

max_stat = 150
max_stat_norm = max_stat / 10
race_energy_loss_per_tick = 10  # base energy loss per tick


def simulate_single_race(horses, track, track_data, corner_indices):
    track_length = track["track_steps"]
    positions = {h["id"]: 0 for h in horses}

    # Initialize positions & race_energy for each horse
    positions = {h["id"]: 0 for h in horses}
    race_energy = {h["id"]: 100 for h in horses}  # start full energy
    positions_frames = []

    # Precompute energy multipliers
    # energy_multipliers = {}
    # for h in horses:
    #     energy = 1  # Normalize to 0–1
    #     energy = max(energy, 0.001)  # clamp low values
    #     multiplier = 1 + math.log(energy + 0.01) * 0.1
    #     energy_multipliers[h["id"]] = max(0, multiplier)

    steps = 0
    while max(positions.values()) < track_length or steps > 1000:
        steps += 1
        for h in horses:
            horse_id = h["id"]
            progress = positions[horse_id]
            percentage_progress = progress / track_length

            path_index = get_current_track_point([tuple(p) for p in track_data[0]], percentage_progress)
            on_corner = path_index in corner_indices

            # Base stat weights, different on corners
            speed_weight = 2.0
            stamina_weight = 1.2
            agility_weight = .8
            if on_corner:
                agility_weight = 1.8
                speed_weight = 1.5
                stamina_weight = 1.2

            # Normalize stats (0-150 to ~0-15)
            norm_speed = h["speed"] / max_stat_norm
            norm_stamina = h["stamina"] / max_stat_norm
            norm_agility = h["agility"] / max_stat_norm

            # Fatigue penalty (more fatigue with less stamina)
            fatigue_percent = progress / 60
            fatigue_penalty = fatigue_percent * (1 - norm_stamina / max_stat_norm)

            # Effective speed after fatigue
            effective_speed = norm_speed * (1 - 0.3 * fatigue_penalty)

            # Calculate base chance to move this tick
            chance = (
                (effective_speed * speed_weight) +
                (norm_stamina * stamina_weight) +
                (norm_agility * agility_weight)
            ) / 30

            # Apply permanent energy multiplier
            #chance *= energy_multipliers[horse_id]

            # Apply randomness to chance for natural variation
            chance *= random.uniform(0.9, 1.1)
            chance = min(chance, 0.95)  # cap max chance

            # Reduce race energy every tick based on stamina (higher stamina = less loss)
            energy_loss = race_energy_loss_per_tick * (1 - (h["stamina"] / max_stat))
            race_energy[horse_id] = max(0, race_energy[horse_id] - energy_loss)

            # === BURST MECHANIC ===
            burst_steps = 1  # default move 1 step

            # Randomize burst chance based on stamina with some variation
            base_burst_chance = 0.05 + (h["stamina"] / max_stat) * 0.2
            burst_chance = random.uniform(base_burst_chance * 0.7, base_burst_chance * 1.3)
            burst_chance = min(burst_chance, 0.3)

            if race_energy[horse_id] > 10 and random.random() < burst_chance:
                max_burst = 1 + int((h["agility"] / max_stat) * 2)  # max 3 steps burst
                # Weighted random burst steps: mostly small bursts, less big
                burst_steps = random.choices(
                    population=[1, 2, 3],
                    weights=[0.7, 0.2, 0.1],
                    k=1
                )[0]
                burst_steps = min(burst_steps, max_burst)

                # Variable energy cost per burst step
                energy_cost = (burst_steps - 1) * random.randint(4, 6)

                # Reduce burst steps if not enough energy
                while burst_steps > 1 and race_energy[horse_id] < energy_cost:
                    burst_steps -= 1
                    energy_cost = (burst_steps - 1) * random.randint(4, 6)

                # Deduct energy if burst
                if burst_steps > 1:
                    race_energy[horse_id] -= energy_cost

            # Final movement roll
            if random.random() < chance:
                positions[horse_id] += burst_steps

    # Find winner
    return max(positions, key=positions.get)

def calculate_odds_defaults(horses, track):
    track_data = db.get_track_data(track)
    corner_indices = track_data[-1].get("corner_indices", []) if isinstance(track_data[-1], dict) else []

    return calculate_odds_by_simulation(horses, track, track_data, corner_indices)

def calculate_odds_by_simulation(horses, track, track_data, corner_indices, simulations=1000, house_edge=0.05):
    """
    Calculate odds by simulating races.
    
    house_edge: fraction taken by the house (e.g. 0.05 = 5%)
    """
    track_length = track["track_steps"]

    win_counts = {h["id"]: 0 for h in horses}

    for _ in range(simulations):
        winner_id = simulate_single_race(horses, track, track_data, corner_indices)
        win_counts[winner_id] += 1

    total = sum(win_counts.values())
    odds = {}
    for horse_id, wins in win_counts.items():
        prob = wins / total
        if prob > 0:
            fair_odds = 1 / prob
            # Apply house edge to payout odds (reduce payouts)
            payout_odds = round(fair_odds * (1 - house_edge), 2)
            payout_odds = min(payout_odds, float(200.0))
            house_payout = round(1 - prob * payout_odds, 4)
        else:
            payout_odds = float(500.0)  # practically impossible to win
            house_payout = 1.0
        odds[horse_id] = {"probability": prob, "decimal_odds": payout_odds, "house_payout": house_payout}

    return odds