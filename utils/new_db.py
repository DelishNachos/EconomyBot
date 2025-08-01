import os
import json
import boto3
from boto3.dynamodb.conditions import Attr
from pathlib import Path
import random

from utils.horse_generator import generate_daily_horses

ENV = os.getenv("ENVIRONMENT", "local")
IS_LOCAL = ENV == "local"
LOCAL_DB_PATH = Path("C:\Users\Ian\Documents\DiscordBots\HorseRacingBotData/local_db.json")
HORSE_DATA_PATH = Path("C:\Users\Ian\Documents\DiscordBots\HorseRacingBotData/horses.json")

DAILY_DATA_ID = os.getenv("DAILY_DATA_ID")