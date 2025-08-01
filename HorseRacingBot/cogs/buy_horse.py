import discord
from discord.ext import commands
from discord.ui import View, Button
from utils.horse_generator import generate_random_horse
from utils.json_helper import load_json, save_json
import json
from pathlib import Path
from utils import db

DAILY_HORSES_FILE = Path("data/daily_horses.json")
DAILY_HORSES_FILE.parent.mkdir(exist_ok=True)


HORSES_PATH = Path("data/horses.json")
USERS_PATH = Path("data/local_db.json")

def load_daily_horses():
    if DAILY_HORSES_FILE.exists():
        return json.load(open(DAILY_HORSES_FILE))
    else:
        horses = [generate_random_horse() for _ in range(3)]
        json.dump(horses, open(DAILY_HORSES_FILE, "w"), indent=2)
        return horses

def save_daily_horses(horses):
    json.dump(horses, open(DAILY_HORSES_FILE, "w"), indent=2)

class HorseSelectView(View):
    def __init__(self, horses, callback):
        super().__init__()
        self.horses = horses
        for i, horse in enumerate(horses):
            self.add_item(HorseButton(label=f"Buy Horse #{i+1}", horse=horse, callback=callback))

class HorseButton(Button):
    def __init__(self, label, horse, callback):
        super().__init__(label=label, style=discord.ButtonStyle.green)
        self.horse = horse
        self.callback_fn = callback

    async def callback(self, interaction: discord.Interaction):
        await self.callback_fn(interaction, self.horse)

class HorseBuying(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="buyhorse", description="Buy one of three available horses.")
    async def buyhorse(self, ctx):
        horses = load_daily_horses()

        embeds = []
        for i, horse in enumerate(horses):
            embed = discord.Embed(title=f"Horse #{i+1}: {horse['name']}", color=discord.Color.blue())
            embed.add_field(name="Speed", value=horse["speed"])
            embed.add_field(name="Stamina", value=horse["stamina"])
            embed.add_field(name="Agility", value=horse["agility"])
            if horse["image_url"]:
                embed.set_thumbnail(url=horse["image_url"])
            embeds.append(embed)

        async def on_buy(interaction, selected_horse):
            user_id = str(ctx.user.id)

            # Load DBs
            horses_db = load_json(HORSES_PATH)
            users_db = load_json(USERS_PATH)

            # 1. Save new horse to horses.json
            selected_horse["owner"] = user_id
            horses_db.append(selected_horse)
            save_json(HORSES_PATH, horses_db)

            # 2. Add horse ID to user in users.json
            if user_id not in users_db:
                users_db[user_id] = db.empty_user_table_item(user_id)

            if "horses" not in users_db[user_id]["stables"]:
                users_db[user_id]["stables"]["horses"] = []

            users_db[user_id]["stables"]["horses"].append(selected_horse["id"])
            save_json(USERS_PATH, users_db)

            # 3. Replace the purchased horse in daily_horses.json
            horses = load_daily_horses()
            horses = [generate_random_horse() if h["id"] == selected_horse["id"] else h for h in horses]
            save_daily_horses(horses)

            await interaction.response.send_message(
                f"You bought **{selected_horse['name']}**!\nUse `/renamehorse` to name it and `/addimage` to upload a picture.",
                ephemeral=True
            )

        await ctx.respond(
            content="Choose a horse to purchase:",
            embeds=embeds,
            view=HorseSelectView(horses, on_buy),
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(HorseBuying(bot))