import os
import discord
from cogs.stable_views.horse_confirm_retire_screen import ConfirmRetireView
from cogs.stable_views.stable_manage_screen import StableManageView
from cogs.stable_views.stables_main_screen import MainStableView
from cogs.stable_views.horses_screen import HorsesScreenView
from cogs.stable_views.stables_upgrade_screen import UpgradeScreenView
from cogs.stable_views.horse_list_screen import HorseListScreenView
from cogs.stable_views.horse_select_screen import HorseSelectView
from cogs.stable_views.horse_manage_screen import HorseManageView
from cogs.stable_views.horse_customize_screen import HorseCustomizeView
from cogs.stable_views.horse_training_screen import HorseTrainingView
from cogs.stable_views.training_views.speed_training_screen import SpeedTrainingView
from cogs.stable_views.training_views.speed_game_screen import SpeedGameView
from cogs.stable_views.training_views.speed_game_end_screen import SpeedGameEndView
from cogs.stable_views.training_views.stamina_training_screen import StaminaTrainingView
from cogs.stable_views.training_views.stamina_game_screen import StaminaGameView
from cogs.stable_views.training_views.stamina_game_end_screen import StaminaGameEndView
from cogs.stable_views.training_views.agility_training_screen import AgilityTrainingView
from cogs.stable_views.training_views.agility_game_screen import AgilityGameView
from cogs.stable_views.training_views.agility_game_end_screen import AgilityGameEndView
from cogs.stable_views.inventory_main_screen import InventoryMainView
from cogs.stable_views.inventory_type_screen import InventoryTypeView
from cogs.stable_views.item_select_screen import ItemSelectView
from cogs.stable_views.item_give_screen import ItemGiveView

from utils import db
from utils import training_calculator


def get_main_stable_view(user_id):
    stable_data = db.get_user_stable_data(user_id)
    return MainStableView(user_id, stable_data)

def get_horses_view(user_id):
    return HorsesScreenView(user_id)

def get_stables_manage_view(user_id):
    return StableManageView(user_id)

def get_stables_upgrade_view(user_id):
    return UpgradeScreenView(user_id)

def get_horse_list_view(user_id):
    return HorseListScreenView(user_id)

def get_horse_select_view(user_id, horses):
    return HorseSelectView(user_id, horses)

def get_horse_manage_view(user_id, horse):
    return HorseManageView(user_id, horse)

def get_horse_customize_view(user_id, horse):
    return HorseCustomizeView(user_id, horse)

def get_horse_training_view(user_id, horse):
    return HorseTrainingView(user_id, horse)

def get_speed_training_view(user_id, horse):
    return SpeedTrainingView(user_id, horse)

def get_speed_game_view(user_id, horse, interaction, on_complete):
    return SpeedGameView(user_id, horse, interaction, on_complete)

def get_speed_game_end_view(user_id, horse):
    return SpeedGameEndView(user_id, horse)

def get_stamina_training_view(user_id, horse):
    return StaminaTrainingView(user_id, horse)

def get_stamina_game_view(user_id, horse, interaction, on_complete):
    return StaminaGameView(user_id, horse, interaction, on_complete)

def get_stamina_game_end_view(user_id, horse):
    return StaminaGameEndView(user_id, horse)

def get_agility_training_view(user_id, horse):
    return AgilityTrainingView(user_id, horse)

def get_agility_game_view(user_id, horse, interaction, on_complete):
    return AgilityGameView(user_id, horse, interaction, on_complete)

def get_agility_game_end_view(user_id, horse):
    return AgilityGameEndView(user_id, horse)

def get_inventory_main_view(user_id):
    return InventoryMainView(user_id)

def get_inventory_type_view(user_id):
    return InventoryTypeView(user_id)

def get_item_select_view(user_id, horse, items):
    return ItemSelectView(user_id, horse, items)

def get_item_give_view(user_id, horse, item):
    return ItemGiveView(user_id, horse, item)

def get_confirm_retire_view(user_id, horse):
    return ConfirmRetireView(user_id, horse)



def main_stable_screen(user_id):
    stable_data = db.get_user_stable_data(user_id)
    stable_level_data = db.get_stable_level_data(stable_data['level'])

    content = None#f"🏠 **{stable_data['name']}**\nHorses: {stable_data['horse_count']}/{stable_level_data['max_horses']}"
    embed = discord.Embed(
        title=f"🏠 {stable_data['name']}",
        description="Manage your horses and upgrade your stables.",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embed.add_field(name="Horses", value=f"{stable_data['horse_count']}/{stable_level_data['max_horses']}", inline=True)
    embed.add_field(name="Stable Income", value=f"${stable_level_data['passive_income']}/hr")
    embed.add_field(name="Horse Income", value=f"${int(db.calculate_total_horse_income(user_id))}/hr")
    #embed.add_field(name="Current Stable Level", value=stable_data['level'], inline = False)
    embed.set_footer(text=f"Stable Level: {stable_data['level']}")
    view = get_main_stable_view(user_id)

    return {
        "content": content,
        "embed": embed,
        "view": view
    }

def stables_manage_screen(user_id):
    stable_data = db.get_user_stable_data(user_id)
    stable_level_data = db.get_stable_level_data(stable_data['level'])

    content = None#f"🏠 **{stable_data['name']}**\nHorses: {stable_data['horse_count']}/{stable_level_data['max_horses']}"
    embed = discord.Embed(
        title=f"🏠 {stable_data['name']}",
        description="Manage your horses and upgrade your stables.",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embed.add_field(name="Horses", value=f"{stable_data['horse_count']}/{stable_level_data['max_horses']}", inline=True)
    embed.add_field(name="Stable Income", value=f"${stable_level_data['passive_income']}/hr")
    embed.add_field(name="Horse Income", value=f"${int(db.calculate_total_horse_income(user_id))}/hr")
    #embed.add_field(name="Current Stable Level", value=stable_data['level'], inline = False)
    embed.set_footer(text=f"Stable Level: {stable_data['level']}")
    view = get_stables_manage_view(user_id)

    return {
            "content": content,
            "embed": embed,
            "view": view
        }

def stables_upgrade_screen(user_id):
   stable_data = db.get_user_stable_data(user_id)
   stable_level_data = db.get_stable_level_data(stable_data['level'])
   next_level_data = db.get_stable_level_data(stable_data['level'] + 1)
   content = None
   embed = discord.Embed(
       title=f"Upgrade Stable",
       description="",
       color=discord.Color.gold()
   ) 
   embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
   embed.add_field(name=f"Horses", value=f"**{stable_data['horse_count']}/{stable_level_data['max_horses']}** --> **{stable_data['horse_count']}/{next_level_data['max_horses']}**", inline=False)
   embed.add_field(name=f"Income", value=f"**${stable_level_data['passive_income']}/hr** --> **${next_level_data['passive_income']}/hr**", inline=False)
   embed.add_field(name="Cost",value=f"**${next_level_data['cost']}**", inline=False)
   view = get_stables_upgrade_view(user_id)

   return {
        "content": content,
        "embed": embed,
        "view": view
    }

def horses_screen(user_id):
    stable_data = db.get_user_stable_data(user_id)
    stable_level_data = db.get_stable_level_data(stable_data['level'])

    content = ""
    embed = discord.Embed(
        title="Horse Menu",
        description="Manage your horses from here.",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embed.add_field(name="Horses", value=f"{stable_data['horse_count']}/{stable_level_data['max_horses']}", inline=True)
    embed.add_field(name="Horse Income", value=f"${int(db.calculate_total_horse_income(user_id))}/hr")
    view = get_horses_view(user_id)

    return {
        "content": content,
        "embed": embed,
        "view": view
    }

def horse_list_screen(user_id):
    horses = db.get_user_horses(user_id)

    if not horses:
        content = "You don't own any horses yet."
        embed = discord.Embed(
            title="Horse List",
            description="Buy or win horses to view them here.",
            color=discord.Color.gold()
        )
        return {
            "content": content,
            "embed": embed,
            "view": get_horse_list_view(user_id)
        }

    embed = discord.Embed(
        title="Your Horses",
        color=discord.Color.blurple()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    for horse in horses:
        name = horse.get("name", "Unknown")
        speed = horse.get("speed", 0)
        stamina = horse.get("stamina", 0)
        agility = horse.get("agility", 0)
        energy = horse.get("energy", "N/A")
        wins = horse.get("wins", 0)
        races = horse.get("races", 0)
        public = horse.get("public", False)
        income = db.calculate_income_of_horse(horse)

        stats_text = (
            f"**Stats:** Speed: {speed}, Stamina: {stamina}, Agility: {agility}\n"
            f"**Energy:** {energy}\n"
            f"🏆 Wins: {wins} | 🐎 Races: {races}\n"
            f"**Public:** {public}"
            f"**Income** ${income}/hr"
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        embed.add_field(name=name, value=stats_text, inline=False)

    return {
        "content": "",  # or a summary string if you'd like
        "embed": embed,
        "view": get_horse_list_view(user_id)
    }

def horse_select_screen(user_id):
    horses = db.get_user_horses(user_id)

    return {
        "content": "",  # or a summary string if you'd like
        "embed": None,
        "view": get_horse_select_view(user_id, horses)
    }

def horse_manage_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse

    content = ""
    embed = discord.Embed(
        title=f"Managing {horse['name']}",
        description="",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    # embed.set_image(url=f"attachment://{filename}")
    embed.set_thumbnail(url=f"attachment://{filename}")
    embed.add_field(name="Speed", value=horse["speed"])
    embed.add_field(name="Stamina", value=horse["stamina"])
    embed.add_field(name="Agility", value=horse["agility"])
    embed.add_field(name="Wins", value=horse["wins"])
    embed.add_field(name="Races", value=horse['races'])
    embed.add_field(name="Energy", value=f"{horse['energy']}%")
    embed.add_field(name="Income", value=f"${db.calculate_income_of_horse(horse)}/hr")
    embed.set_footer(text="Public horses can be selected in all custom and random races (your horse will **not** lose energy when selected)")

    return {
        "content": content,
        "embed": embed,
        "view": get_horse_manage_view(user_id, horse),
        "file": file
    }

def horse_customize_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse

    content = ""
    embed = discord.Embed(
        title=f"Customizing {horse['name']}",
        description="",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    embed.set_image(url=f"attachment://{filename}")

    return {
        "content": content,
        "embed": embed,
        "view": get_horse_customize_view(user_id, horse),
        "file": file
    }

def horse_training_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse

    content = ""
    embed = discord.Embed(
        title=f"Training {horse['name']}",
        description="",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    #embed.set_image(url=f"attachment://{filename}")
    embed.set_thumbnail(url=f"attachment://{filename}")
    embed.add_field(name="Speed", value=horse["speed"] )
    embed.add_field(name="Stamina", value=horse["stamina"] )
    embed.add_field(name="Agility", value=horse["agility"])
    embed.add_field(name="Energy", value=f"{horse['energy']}%", inline=False)

    return {
        "content": content,
        "embed": embed,
        "view": get_horse_training_view(user_id, horse),
        "file": file
    }

def speed_training_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse

    content = ""
    embed = discord.Embed(
        title=f"Speed Training",
        description="",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    #embed.set_image(url=f"attachment://{filename}")
    embed.set_thumbnail(url=f"attachment://{filename}")
    embed.add_field(name="Current Energy", value=f"{horse['energy']}%", inline=False)
    embed.add_field(name="Current Speed", value=horse["speed"], inline=True)
    embed.add_field(name="", value="")
    embed.add_field(name="Possible Gain", value=f"~{training_calculator.calculate_speed_gain(horse['speed'], 12)}", inline = True)
    embed.add_field(name="Cost", value=f"${training_calculator.calculate_cost(horse['speed'])}")
    embed.add_field(name="", value="")
    embed.add_field(name="Energy Cost", value=f"{training_calculator.calculate_energy(horse['speed'])}%")

    return {
        "content": content,
        "embed": embed,
        "view": get_speed_training_view(user_id, horse),
        "file": file
    }

async def speed_game_screen(interaction: discord.Interaction, user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
    
    async def on_game_complete(taps, interaction):
        points = training_calculator.calculate_speed_gain(horse["speed"], taps)
        cost = training_calculator.calculate_cost(horse["speed"])
        energy_cost = training_calculator.calculate_energy(horse["speed"])

        horse["speed"] = min(horse["speed"] + points, 150)
        db.update_balance(user_id, -cost)
        horse["energy"] -= energy_cost
        db.update_horse(horse)

        embed = discord.Embed(
            title="🏁 Speed Training Complete!",
            description=(
                f"🖱️ You tapped **{taps}** times!\n"
                f"📈 Speed gained: **{points}**\n"
                f"💸 Cost: ${cost}\n"
                f"⚡ Energy Used: {energy_cost}%"
            ),
            color=discord.Color.green()
        )
        embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

        # Extract filename from the stored image_url path
        filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
        
        if filename and os.path.exists(horse["image_url"]):
            file = discord.File(horse["image_url"], filename=filename)
        else:
            file = discord.File(db.default_horse_image_path(), filename=filename)

        embed.set_thumbnail(url=f"attachment://{filename}")


        await interaction.edit_original_response(
            embed=embed,
            view=get_speed_game_end_view(user_id, horse),
            content=None,
            file=file
        )

    embed = discord.Embed(
        title="Speed Training",
        description="Tap the button as fast as you can!",
        color=discord.Color.red()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    embed.set_thumbnail(url=f"attachment://{filename}")

    return {
        "embed": embed,
        "view": get_speed_game_view(user_id, horse, interaction, on_game_complete),
        "content": None,
        "file": file
    }

def stamina_training_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
    
    content = ""
    embed = discord.Embed(
        title=f"Stamina Training",
        description="",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    #embed.set_image(url=f"attachment://{filename}")
    embed.set_thumbnail(url=f"attachment://{filename}")
    embed.add_field(name="Current Energy", value=f"{horse['energy']}%", inline=False)
    embed.add_field(name="Current Stamina", value=horse["stamina"], inline=True)
    embed.add_field(name="", value="")
    embed.add_field(name="Max Gain", value=f"{training_calculator.calculate_stamina_gain(horse['stamina'], 3.0, 3.0)}", inline = True)
    embed.add_field(name="Cost", value=f"${training_calculator.calculate_cost(horse['stamina'])}")
    embed.add_field(name="", value="")
    embed.add_field(name="Energy Cost", value=f"{training_calculator.calculate_energy(horse['stamina'])}%")

    return {
        "content": content,
        "embed": embed,
        "view": get_stamina_training_view(user_id, horse),
        "file": file
    }

async def stamina_game_screen(interaction: discord.Interaction, user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
    
    target_time = 3.0  # Ideal hold time in seconds

    async def on_game_complete(hold_time, interaction):
        points = training_calculator.calculate_stamina_gain(horse['stamina'], hold_time, target_time)
        cost = training_calculator.calculate_cost(horse["stamina"])
        energy_cost = training_calculator.calculate_energy(horse["stamina"])

        horse["stamina"] = min(horse["stamina"] + points, 150)
        db.update_balance(user_id, -cost)
        horse["energy"] -= energy_cost
        db.update_horse(horse)

        embed = discord.Embed(
            title="💪 Stamina Training Complete!",
            description=(
                f"⏱️ You held for **{hold_time:.2f}** seconds\n"
                f"🎯 Target was **{target_time}** seconds\n"
                f"📈 Stamina gained: **{points}**\n"
                f"💸 Cost: ${cost}\n"
                f"⚡ Energy Used: {energy_cost}%"
            ),
            color=discord.Color.green()
        )
        embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

        filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
        file = discord.File(horse["image_url"], filename=filename) if filename and os.path.exists(horse["image_url"]) else discord.File(db.default_horse_image_path(), filename=filename)
        embed.set_thumbnail(url=f"attachment://{filename}")

        await interaction.edit_original_response(
            embed=embed,
            view=get_stamina_game_end_view(user_id, horse),
            content=None,
            file=file
        )

    embed = discord.Embed(
        title="Stamina Training",
        description="🎯 Try to hold the button for exactly 3 seconds!\nClick once to start, again to release.",
        color=discord.Color.red()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    file = discord.File(horse["image_url"], filename=filename) if filename and os.path.exists(horse["image_url"]) else discord.File(db.default_horse_image_path(), filename=filename)
    embed.set_thumbnail(url=f"attachment://{filename}")

    return {
        "embed": embed,
        "view": get_stamina_game_view(user_id, horse, interaction, on_game_complete),
        "content": None,
        "file": file
    }

def agility_training_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
    
    content = ""
    embed = discord.Embed(
        title=f"Agility Training",
        description="",
        color=discord.Color.gold()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    #embed.set_image(url=f"attachment://{filename}")
    embed.set_thumbnail(url=f"attachment://{filename}")
    embed.add_field(name="Current Energy", value=f"{horse['energy']}%", inline=False)
    embed.add_field(name="Current Agility", value=horse["agility"], inline=True)
    embed.add_field(name="", value="")
    embed.add_field(name="Max Gain", value=training_calculator.calculate_agility_gain(horse['agility'], 0), inline = True)
    embed.add_field(name="Cost", value=f"${training_calculator.calculate_cost(horse['agility'])}")
    embed.add_field(name="", value="")
    embed.add_field(name="Energy Cost", value=f"{training_calculator.calculate_energy(horse['agility'])}%")

    return {
        "content": content,
        "embed": embed,
        "view": get_agility_training_view(user_id, horse),
        "file": file
    }

async def agility_game_screen(interaction: discord.Interaction, user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
   
    async def on_game_complete(success, reaction_time, interaction):
        points = training_calculator.calculate_agility_gain(horse["agility"], reaction_time)
        cost = training_calculator.calculate_cost(horse["agility"])
        energy_cost = training_calculator.calculate_energy(horse["agility"])

        if success:
            horse["agility"] = min(horse["agility"] + points, 150)

        db.update_balance(user_id, -cost)
        horse["energy"] -= energy_cost
        db.update_horse(horse)

        description = (
            f"✅ Success! You reacted in **{reaction_time:.2f}s**.\n"
            if success else
            f"❌ Too early! You clicked before the signal.\n"
        )

        embed = discord.Embed(
            title="🌀 Agility Training Complete!",
            description=(
                description +
                f"📈 Agility gained: **{points if success else 0}**\n"
                f"💸 Cost: ${cost}\n"
                f"⚡ Energy Used: {energy_cost}%"
            ),
            color=discord.Color.green() if success else discord.Color.red()
        )
        embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

        filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
        file = discord.File(horse["image_url"], filename=filename) if filename and os.path.exists(horse["image_url"]) else discord.File(db.default_horse_image_path(), filename=filename)
        embed.set_thumbnail(url=f"attachment://{filename}")

        await interaction.edit_original_response(
            embed=embed,
            view=get_agility_game_end_view(user_id, horse),
            content=None,
            file=file
        )

    embed = discord.Embed(
        title="Agility Training",
        description="Wait for the signal, then click the button as fast as you can!",
        color=discord.Color.red()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    file = discord.File(horse["image_url"], filename=filename) if filename and os.path.exists(horse["image_url"]) else discord.File(db.default_horse_image_path(), filename=filename)
    embed.set_thumbnail(url=f"attachment://{filename}")

    return {
        "embed": embed,
        "view": get_agility_game_view(user_id, horse, interaction, on_game_complete),
        "content": None,
        "file": file
    }

def inventory_main_screen(user_id):
    inventory = db.get_user(user_id).get('inventory', [])
    embed_description = "You can view all your items here"

    if not inventory:
        embed_description = "Your inventory is empty"

    content = ""
    embed = discord.Embed(
        title="📦 Inventory",
        description=embed_description,
        color=discord.Color.blue()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    return {
        "content": content,
        "embed": embed,
        "view": get_inventory_main_view(user_id)
    }

def inventory_type_screen(user_id, item_type):
    inventory = db.get_user(user_id).get('inventory', [])

    embeds = []

    content = None
    embed = discord.Embed(
        title=f"Your {item_type} item(s)",
        description="",
        color=discord.Color.blue()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embeds.append(embed)

    items = db.get_items_by_type(item_type)

    for entry in inventory:
        item = db.get_item_by_id(entry['item'])
        if item['type'] == item_type:
            embed = discord.Embed(title=f"{item['name']} (X{db.get_user_item_count(user_id, item)})", description=item['description'], color=discord.Color.blue())
            embed.add_field(name="Energy Recovery", value=f"{item['energy']}%")
            embed.add_field(name="", value = "")
            embeds.append(embed)

    return {
        "content": content,
        "embeds": embeds,
        "view": get_inventory_type_view(user_id)
    }

def item_select_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse

    items = db.get_user_items(user_id)

    return {
        "content": "",  # or a summary string if you'd like
        "embed": None,
        "view": get_item_select_view(user_id, horse, items)
    }

def item_give_screen(user_id, horse, item):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
    # updates horse
    horse_id = horse['id']
    horse = db.get_horse_by_id(horse_id)

    content = ""
    embed = discord.Embed(
        title=f"Giving {horse['name']} {item['name']}",
        description="",
        color=discord.Color.blue()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    # Extract filename from the stored image_url path
    filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
    
    if filename and os.path.exists(horse["image_url"]):
        file = discord.File(horse["image_url"], filename=filename)
    else:
        file = discord.File(db.default_horse_image_path(), filename=filename)

    # embed.set_image(url=f"attachment://{filename}")
    embed.set_thumbnail(url=f"attachment://{filename}")
    embed.add_field(name="Current Energy", value=f"{horse['energy']}%")
    embed.add_field(name="", value="")
    embed.add_field(name="After Energy", value=f"{min(100, (horse['energy'] + item['energy']))}%")
    embed.add_field(name="Item Amount", value=f"{db.get_user_item_count(user_id, item)}")

    return {
        "content": content,
        "embed": embed,
        "view": get_item_give_view(user_id, horse, item),
        "file": file
    }

def horse_retire_confirm_screen(user_id, horse):
    refreshed_horse = db.get_horse_by_id(horse['id'])
    horse = refreshed_horse
    content = None
    embed = discord.Embed(
        title=f"Are you sure you want to retire this horse?",
        description="You will not be able to undo this action",
        color=discord.Color.red()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    return {
        "content": content,
        "embed": embed,
        "view": get_confirm_retire_view(user_id, horse)
    }