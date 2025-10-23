import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from utils import db


# Load either .env or .env.production
if os.path.exists('.env'):
    load_dotenv('.env')
# else:
#     load_dotenv('.env.production')

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(id) for id in os.getenv("DISCORD_GUILD_ID").split(",")]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
db.GLOBAL_BOT = bot

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.sync_commands(guild_ids=GUILD_IDS)

# Load all cogs
for extension in ["cogs.economy", "cogs.horserace", "cogs.stable_manager", "cogs.shop_manager", "cogs.racetrack_manager", "cogs.daily_horse_refresh", "cogs.bank_manager", "cogs.help"]:
    bot.load_extension(extension)

bot.run(TOKEN)