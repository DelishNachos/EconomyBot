from utils import db

AVG_TAPS = 12

def calculate_speed_gain(current_speed, taps):
    raw_points = (10 - (AVG_TAPS // 2)) + (taps // 2)

    return diminished_stat_gain(raw_points, current_speed)

def calculate_stamina_gain(current_stamina, hold_time, target_time):
    difference = abs(hold_time - target_time)
    max_points = 10
    raw_points = max(0, int(max_points * (1 - (difference / target_time))))

    return diminished_stat_gain(raw_points, current_stamina)

def calculate_agility_gain( current_agility, reaction_time):

    if reaction_time < 1:
        base_gain = 10
    elif reaction_time < 1.5:
        base_gain = 8
    elif reaction_time < 1.7:
        base_gain = 6
    elif reaction_time < 2.0:
        base_gain = 4
    elif reaction_time < 2.5:
        base_gain = 2
    else:
        base_gain = 0

    # Apply diminishing returns based on current agility
    return diminished_stat_gain(base_gain, current_agility)



def calculate_cost(current_stat):
    return db.get_general_config()['base_training_cost'] + (current_stat * 3)

def calculate_energy(current_stat):
    return db.get_general_config()['base_training_energy'] + (current_stat // 15)

def diminished_stat_gain(raw_gain, current_stat):
    diminishing_multiplier = 1 - (current_stat / 150)
    return max(1, int(raw_gain * diminishing_multiplier))