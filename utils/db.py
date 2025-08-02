import datetime
import glob
import os
import json
from pathlib import Path
import random
from PIL import Image

from utils import horse_generator, race_horse_manager
from utils.horse_generator import generate_daily_horses

# Current file's directory
BOT_DIR = Path(__file__).resolve().parent.parent

# Go to sibling HorseRacingBotData/Data
DATA_PATH = BOT_DIR.parent / "HorseRacingBotData" / "Data"
ASSETS_PATH = BOT_DIR.parent / "HorseRacingBotData" / "Assets"

LOCAL_DB_PATH = DATA_PATH / "local_db.json"
HORSE_DATA_PATH = DATA_PATH / "horses.json"
DAILY_HORSE_DATA_PATH = DATA_PATH / "daily_horses.json"
STABLE_LEVEL_PATH = DATA_PATH / "stables_level.json"
ITEMS_PATH = DATA_PATH / "horse_items.json"
HORSE_RACING_CONFIG_PATH = DATA_PATH / "horse_racing_config.json"
TRACKS_PATH = DATA_PATH /  "tracks.json"
TRACK_DATA_PATH = DATA_PATH / "tracks"
GENERAL_CONFIG_PATH = DATA_PATH / "general_config.json"

GLOBAL_BOT = None

def ensure_user_exists(user_id):
    user_id = str(user_id)
    with open(LOCAL_DB_PATH, "r") as f:
        users = json.load(f)

    if user_id not in users:
        users[user_id] = empty_user_table_item(user_id)
        with open(LOCAL_DB_PATH, "w") as f:
            json.dump(users, f, indent=2)

def load_users():
    with open(LOCAL_DB_PATH, "r") as f:
        data = json.load(f)
    return data

def get_user(user_id):
    user_id = str(user_id)
    with open(LOCAL_DB_PATH, "r") as f:
        users = json.load(f)

    if user_id not in users:
        users[user_id] = empty_user_table_item(user_id)
        with open(LOCAL_DB_PATH, "w") as f:
            json.dump(users, f, indent=2)

    return users[user_id]

async def get_user_name(user_id):
    guild_id = int(os.getenv("DISCORD_GUILD_ID"))
    guild = GLOBAL_BOT.get_guild(guild_id) or await GLOBAL_BOT.fetch_guild(guild_id)
    member = guild.get_member(user_id) or await guild.fetch_member(user_id)

    return member.display_name

def get_balance(user_id):
    return get_user(user_id).get("balance", 0)

def update_balance(user_id, amount):
    ensure_user_exists(user_id)
    user_id = str(user_id)
    with open(LOCAL_DB_PATH, "r") as f:
        data = json.load(f)

    user_data = data[user_id]
    user_data["balance"] += amount
    data[user_id] = user_data

    with open(LOCAL_DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def update_user(user_data):
    user_id = user_data["user_id"]
    
    # Load current database
    with open(LOCAL_DB_PATH, "r") as f:
        users = json.load(f)

    # Update the specific user's data
    users[user_id] = user_data

    # Save the updated database
    with open(LOCAL_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)

def calculate_per_hour_income(user_id):
    horses = get_user_horses(user_id)
    stable_data = get_user_stable_data(user_id)
    stable_level_data = get_stable_level_data(stable_data['level'])

    total_horse_income = calculate_total_horse_income(user_id)

    money_for_stable = stable_level_data['passive_income']

    total_money_per_hour = total_horse_income + money_for_stable
    return total_money_per_hour

def calculate_total_horse_income(user_id):
    horses = get_user_horses(user_id)
    return sum(calculate_income_of_horse(h) for h in horses)

def update_saved_income(user_id):
    user  = get_user(user_id)
    now = datetime.datetime.now(datetime.timezone.utc)
     # Parse the timestamps if they exist
    last_updated_time = (
        datetime.datetime.fromisoformat(user['last_income']) if user['last_income'] else now
    )
    last_claimed_time = (
        datetime.datetime.fromisoformat(user['last_claimed']) if user['last_claimed'] else now
    )

    max_earn_time = min(now, last_claimed_time + datetime.timedelta(hours=24))
    capped_delta = (max_earn_time - last_updated_time).total_seconds() / 3600

    if capped_delta > 0:
        income = calculate_per_hour_income(user_id) * capped_delta
        user['saved_income'] += int(income)
        user['last_income'] = now.isoformat()

    update_user(user)

def reset_saved_income(user_id):
    user = get_user(user_id)
    user['saved_income'] = 0
    update_user(user)

def claim_income(user_id):
    update_saved_income(user_id)

    user = get_user(user_id)
    now = datetime.datetime.now(datetime.timezone.utc)

    income_to_claim = user['saved_income']
    user['last_claimed'] = now.isoformat()
    update_user(user)
    reset_saved_income(user_id)
    update_balance(user_id, int(income_to_claim))
    return income_to_claim

def get_updated_saved_income(user_id):
    update_saved_income(user_id)

    user = get_user(user_id)
    return user['saved_income']

def empty_user_table_item(user_id):
    return {
        "user_id": user_id,
        "balance": 0,
        "stables": {
            "name": "Unnamed Stable",
            "horses": [],
            "horse_count": 0,
            "level": 1
        },
        "inventory":[

        ],
        "data_cached": False,
        "last_daily": None,
        "last_income": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "saved_income": 0,
        "last_claimed": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }





def load_all_horses():
    with open(HORSE_DATA_PATH, "r") as f:
        data = json.load(f)
        return data.get("horses", [])

def load_daily_horses():
    with open(DAILY_HORSE_DATA_PATH, "r") as f:
        data = json.load(f)
    if not data:
        daily_horses = generate_daily_horses()
        data = daily_horses
        with open(DAILY_HORSE_DATA_PATH, "w") as f:
            json.dump(data, f, indent=2)
    return data

def get_horse_by_id(horse_id):
    horse_id = str(horse_id)
    horses = load_all_horses()
    for horse in horses:
        if horse["id"] == horse_id:
            race_horse_manager.regenerate_energy(horse)
            return horse
    return None

def get_random_public_horses(count=3, exclude_ids=None):
    exclude_ids = exclude_ids or set()
    horses = load_all_horses()
    public_horses = [h for h in horses if h.get("public") and h["id"] not in exclude_ids]
    
    for horse in public_horses:
        race_horse_manager.regenerate_energy(horse)

    return random.sample(public_horses, min(count, len(public_horses)))

def update_horse(horse):
    horse_id = horse['id']
    with open(HORSE_DATA_PATH, "r") as f:
        data = json.load(f)
    for section in ["horses", "daily_horses"]:
        for i, existing_horse in enumerate(data.get(section, [])):
            if existing_horse["id"] == horse_id:
                data[section][i].update(horse)
                break
    with open(HORSE_DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    horse_owner = horse.get('owner')
    if horse_owner and horse_owner != 'house':
        update_saved_income(horse_owner)
    
def get_user_horses(user_id):
    return [get_horse_by_id(hid) for hid in get_user(user_id).get("stables", {}).get("horses", [])]

def get_user_public_horses(user_id):
    return [horse for horse in get_user_horses(user_id) if horse and horse.get("public", False)]

def add_horse(user_id, horse, to_daily):
    horse['owner'] = str(user_id)
    with open(HORSE_DATA_PATH, "r") as f:
        data = json.load(f)
    key = "daily_horses" if to_daily else "horses"
    data.setdefault(key, []).append(horse)
    with open(HORSE_DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_horse_to_user(user_id, horse):
    horse_id = horse['id']
    user = get_user(user_id)
    if horse_id not in user["stables"]["horses"]:
        user["stables"]["horses"].append(horse_id)
        user['stables']['horse_count'] += 1
    update_user(user)
    update_saved_income(user_id)

def remove_horse_from_user(user_id, horse):
    horse_id = horse['id']
    user = get_user(user_id)
    if horse_id in user["stables"]["horses"]:
        user["stables"]["horses"].remove(horse_id)
        user["stables"]["horse_count"] -= 1

    update_user(user)
    update_saved_income(user_id)
    
def remove_daily_horse(horse_id):
    with open(DAILY_HORSE_DATA_PATH, "r") as f:
        data = json.load(f)
    updated_data = [horse for horse in data if horse["id"] != horse_id]
    with open(DAILY_HORSE_DATA_PATH, "w") as f:
        json.dump(updated_data, f, indent=2)

def refresh_daily_horses():
    horses = horse_generator.generate_daily_horses()
    with open(DAILY_HORSE_DATA_PATH, "w") as f:
        json.dump(horses, f, indent=2)

def calculate_income_of_horse(horse):
    base_money = get_general_config()['money_per_horse']
    money_per_25_stat = get_general_config()['money_per_25_stat']
    total_stats = horse['speed'] + horse['stamina'] + horse['agility']
    total_stat_pools = total_stats // 25
    return base_money + (total_stat_pools * money_per_25_stat)
    
def buy_horse(user_id, horse):
    add_horse(user_id, horse, False)
    add_horse_to_user(user_id, horse)
    remove_daily_horse(str(horse["id"]))
    update_balance(user_id, -horse['market_price'])

def can_buy_horse(user_id, horse):
    if get_balance(user_id) < horse['market_price']:
        return False, "balance"
    user_data = get_user(user_id)
    horse_count = user_data['stables']['horse_count']
    horse_max = get_stable_level_data(user_data['stables']['level'])['max_horses']
    if horse_count >= horse_max:
        return False, "max_horses"
    return True, ""

def give_horse_item(horse, item):
    energy = min(horse['energy'] + item['energy'], 100)
    horse['energy'] = energy
    update_horse(horse)

def empty_horse_table_item(horse_id):
    return {
        "id": str(horse_id),
        "name": "Unnamed Horse",
        "speed": 0,
        "stamina": 0,
        "agility": 0,
        "owner": "",
        "image_url": "assets/horses/OkosanHorse.png",
        "wins": 0,
        "races": 0,
        "energy": 100,
        "public": True,
        "last_energy_update": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "market_price": 0
    }

def default_horse_image_path():
    return ASSETS_PATH / "horses" / "default_horse.png"

def load_horse_image(horse_id, size):
    horse_dir = os.path.join(ASSETS_PATH, "horses")
    pattern = os.path.join(horse_dir, f"{horse_id}.*")
    matches = glob.glob(pattern)

    if matches:
        path = matches[0]  # Use the first match
    else:
        path = default_horse_image_path()

    img = Image.open(path).convert("RGBA").resize(size)
    return img



def load_tracks():
    with open(TRACKS_PATH, "r") as f:
        return json.load(f)

def get_random_race_track():
    tracks = load_tracks()
    return random.sample(tracks, 1)[0]

def get_oval_track():
    return next((t for t in load_tracks() if t["id"] == "oval_horse_track"), None)

def get_track_by_id(track_id):
    tracks = load_tracks()
    for track in tracks:
        if track["id"] == track_id:
            return track
    return None

def get_track_data_from_id(track_id: str):
    with open(f"{TRACK_DATA_PATH}/{track_id}.json") as f:
        return json.load(f)
    
def get_track_data(track):
    track_id = track["id"]
    return get_track_data_from_id(track_id)

def get_track_tags_as_string(track):
    return ', '.join(track['tags'])



def get_user_stable_data(user_id):
    return get_user(user_id).get("stables")

def get_stable_level_data(level):
    with open(STABLE_LEVEL_PATH, "r") as f:
        return json.load(f).get(str(level))

def update_stable_data(user_id, stable_data):
    with open(LOCAL_DB_PATH, "r") as f:
        data = json.load(f)
    user_data = data.get(user_id, {"user_id": user_id, "balance": 0})
    user_data["stables"] = stable_data
    data[user_id] = user_data
    with open(LOCAL_DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def upgrade_stable_data(user_id):
    user = get_user(user_id)
    stored_level = user['stables']['level']
    cost = get_stable_level_data(stored_level)['cost']
    user['stables']['level'] += 1
    update_user(user)
    update_balance(user_id, -cost)
    update_saved_income(user_id)

def can_upgrade_stable(user_id):
    balance = get_balance(user_id)
    stable_data = get_user_stable_data(user_id)
    next_level_data = get_stable_level_data(stable_data['level'] + 1)
    return balance >= next_level_data['cost']



def load_items():
    with open(ITEMS_PATH, "r") as f:
        return json.load(f)
    
def get_item_by_id(item_id):
    items = load_items()
    return items.get(item_id, {})

def get_item_types():
    items = load_items()
    return list({item['type'] for item in items.values()})

def get_user_item_types(user_id):
    inventory = get_user(user_id).get('inventory', [])
    item_types = set()

    for entry in inventory:
        item_id = entry["item"]
        item = get_item_by_id(item_id)
        if item:
            item_types.add(item["type"])

    return item_types

def get_user_items(user_id):
    inventory = get_user(user_id).get('inventory', [])
    items = []

    for entry in inventory:
        item_id = entry["item"]
        item = get_item_by_id(item_id)
        items.append(item)

    return items

def get_items_by_type(item_type):
    items = load_items()
    return [item for item in items.values() if item.get("type") == item_type]

def get_user_item_count(user_id, item):
    inventory = get_user(user_id).get('inventory', [])
    if not inventory:
        return 0
    
    for entry in inventory:
        item_id = entry['item']
        if item_id == item['id']:
            return entry['amount']
        
    return 0

def add_item_to_user(user_id, item):
    user_data = get_user(user_id)
    inventory = user_data.get('inventory', [])
    item_id = item['id']

     # Check if the item is already in the inventory
    for entry in inventory:
        if entry["item"] == item_id:
            entry["amount"] += 1
            break
    else:
        # Item not found; add new entry
        inventory.append({"item": item_id, "amount": 1})

    user_data['inventory'] = inventory
    update_user(user_data)

def remove_item_from_user(user_id, item):
    user_data = get_user(user_id)
    inventory = user_data.get('inventory', [])
    item_id = item['id']

    for entry in inventory:
        if entry["item"] == item_id:
            entry["amount"] -= 1
            if entry["amount"] <= 0:
                inventory.remove(entry)
            break
    else:
        # Item not found, you could raise an error or silently fail
        print(f"Item {item_id} not found in user {user_id}'s inventory.")

    user_data['inventory'] = inventory
    update_user(user_data)

def buy_item(user_id, item):
    add_item_to_user(user_id, item)
    update_balance(user_id, -item['cost'])

def can_buy_item(user_id, item):
    balance = get_balance(user_id)
    return balance >= item['cost']

def use_item(user_id, horse, item):
    remove_item_from_user(user_id, item)
    give_horse_item(horse, item)



def load_horse_race_config():
    with open(HORSE_RACING_CONFIG_PATH, "r") as f:
        config = json.load(f)
    return config

def get_horse_racing_caliber_info():
    config = load_horse_race_config()
    return config["caliber_info"]

def get_horse_racing_caliber_info_by_caliber(caliber):
    caliber_info = get_horse_racing_caliber_info()
    return caliber_info[caliber]

def get_horse_racing_bias_settings():
    config = load_horse_race_config()
    return config["track_biases"]



def get_general_config():
    with open(GENERAL_CONFIG_PATH, "r") as f:
        config = json.load(f)
    return config
