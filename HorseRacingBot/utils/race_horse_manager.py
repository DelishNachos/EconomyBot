import json
import random
from pathlib import Path
from utils import db

def load_horses():
    return db.load_all_horses()

def select_random_race_horses(count=3):
    return db.get_random_public_horses(count)

def get_horse_by_id(horse_id):
    return db.get_horse_by_id(horse_id)

