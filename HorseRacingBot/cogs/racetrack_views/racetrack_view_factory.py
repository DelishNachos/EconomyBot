import os
import discord
from cogs.racetrack_views.racetrack_custom_horse_select_screen import RacetrackCustomHorseSelectView
from cogs.racetrack_views.racetrack_custom_race_results_screen import RacetrackCustomResultsView
from cogs.racetrack_views.racetrack_custom_race_screen import RacetrackCustomRaceView
from cogs.racetrack_views.racetrack_custom_track_select_screen import RacetrackCustomTrackSelectView
from cogs.racetrack_views.racetrack_custom_user_select_screen import RacetrackCustomUserSelectView, UserDropdown
from cogs.racetrack_views.racetrack_main_screen import RacetrackMainView
from cogs.racetrack_views.racetrack_heat_select_screen import RacetrackHeatSelectView
from cogs.racetrack_views.racetrack_heat_info_screen import RacetrackHeatInfoView
from cogs.racetrack_views.racetrack_pre_race_screen import RacetrackPreRaceView
from cogs.racetrack_views.confirm_back_screen import ConfirmLeaveView
from cogs.racetrack_views.racetrack_horse_select_screen import RaceTrackHorseSelectView
from cogs.racetrack_views.racetrack_results_screen import RaceTrackResultsView
from utils import db



def get_racetrack_main_view(user_id):
    return RacetrackMainView(user_id)

def get_racetrack_heat_select_view(user_id):
    return RacetrackHeatSelectView(user_id)

def get_racetrack_heat_info_view(user_id, caliber):
    return RacetrackHeatInfoView(user_id, caliber)

def get_racetrack_pre_race_view(user_id, race_info):
    return RacetrackPreRaceView(user_id, race_info)

def get_confirm_back_view(user_id, race_info):
    return ConfirmLeaveView(user_id, race_info)

def get_racetrack_horse_select_view(user_id, horses, race_info):
    return RaceTrackHorseSelectView(user_id, horses, race_info)

def get_racetrack_results_view(user_id):
    return RaceTrackResultsView(user_id)

def get_racetrack_custom_race_view(user_id, custom_race_info):
    return RacetrackCustomRaceView(user_id, custom_race_info)

def get_racetrack_custom_track_select_view(user_id, tracks, custom_race_info):
    return RacetrackCustomTrackSelectView(user_id, tracks, custom_race_info)

async def get_racetrack_custom_user_select_view(user_id, users, custom_race_info, custom_horse_id):
    dropdown = await UserDropdown.create(user_id, users, custom_race_info, custom_horse_id)
    return RacetrackCustomUserSelectView(user_id, dropdown, custom_race_info)

def get_racetrack_custom_horse_select_view(user_id, horses, custom_race_info, custom_horse_id):
    return RacetrackCustomHorseSelectView(user_id, horses, custom_race_info, custom_horse_id)

def get_racetrack_custom_race_results_view(user_id, is_ephemeral):
    return RacetrackCustomResultsView(user_id, is_ephemeral)



def racetrack_main_screen(user_id):
    content = None
    embed = discord.Embed(
        title=f"Welcome to the racetrack",
        description="Race your horses and earn money here",
        color=discord.Color.orange()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    return {
        "content": content,
        "embed": embed,
        "view": get_racetrack_main_view(user_id)
    }

def racetrack_heat_select_screen(user_id):
    content = None
    embed = discord.Embed(
        title=f"Please select a heat to compete in",
        description="H1 is the pinnacle of horse racing",
        color=discord.Color.orange()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    return {
        "content": content,
        "embed": embed,
        "view": get_racetrack_heat_select_view(user_id)
    }

def racetrack_heat_info_screen(user_id, caliber):
    caliber_info = db.get_horse_racing_caliber_info_by_caliber(caliber)
    min_total, max_total = caliber_info['points']

    content = None
    embed = discord.Embed(
        title=caliber_info['name'],
        description=caliber_info['description'],
        color=discord.Color.orange()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embed.add_field(name="Average total points", value=f"{min_total}-{max_total}", inline=False)
    embed.add_field(name="Cost of entry", value=f"${caliber_info['cost']}")
    embed.add_field(name="Reward for win", value=f"${caliber_info['reward']}")


    return {
        "content": content,
        "embed": embed,
        "view": get_racetrack_heat_info_view(user_id, caliber)
    }

def racetrack_pre_race_screen(user_id, race_info):
    caliber_info = race_info['caliber_info']
    horse = race_info['horse']
    track = race_info['track']

    min_points, max_points = caliber_info['points']
    min_energy, max_energy = caliber_info['energy']

    content = None
    embed = discord.Embed(
        title=f"{caliber_info['name']} Race",
        description="Select a horse and click start when ready",
        color=discord.Color.orange()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    
    embed.add_field(name="----------------------------------------------", value="", inline=False)
    if not horse:
        embed.add_field(name=f"Your Horse - (Horse name)", value="", inline=False)
        embed.add_field(name=f"Speed", value="---")
        embed.add_field(name=f"Stamina", value="---")
        embed.add_field(name=f"Agility", value="---")
        embed.add_field(name=f"Total Stats", value="---")
        embed.add_field(name="", value="")
        embed.add_field(name=f"Energy", value="---")
    else:
        # Extract filename from the stored image_url path
        filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
        
        if filename and os.path.exists(horse["image_url"]):
            file = discord.File(horse["image_url"], filename=filename)
        else:
            file = discord.File(db.default_horse_image_path(), filename=filename)

        embed.set_thumbnail(url=f"attachment://{filename}")
        embed.add_field(name=f"Your Horse - {horse['name']}", value="", inline=False)
        embed.add_field(name=f"Speed", value=horse['speed'])
        embed.add_field(name=f"Stamina", value=horse['stamina'])
        embed.add_field(name=f"Agility", value=horse['agility'])
        embed.add_field(name=f"Total Stats", value=(horse['agility'] + horse['stamina'] + horse['speed']))
        embed.add_field(name="", value="")
        embed.add_field(name=f"Energy", value=f"{horse['energy']}%")


    embed.add_field(name="----------------------------------------------", value="", inline=False)
    embed.add_field(name=f"Track - {track['name']}", value="", inline=False)
    embed.add_field(name="Length", value=track['length'])
    embed.add_field(name="", value="")
    embed.add_field(name="Tags", value=db.get_track_tags_as_string(track))

    embed.add_field(name="----------------------------------------------", value="", inline=False)
    embed.add_field(name="Opponents", value="", inline=False)
    embed.add_field(name="Total Stats", value=f"{min_points}-{max_points}")
    embed.add_field(name="", value="")
    embed.add_field(name="Energy Range", value=f"{min_energy}%-{max_energy}%")

    if not horse:
        return {
        "content": content,
        "embed": embed,
        "view": get_racetrack_pre_race_view(user_id, race_info),
        "attachments": [],
        "file": None
        }
    else:
        return {
        "content": content,
        "embed": embed,
        "view": get_racetrack_pre_race_view(user_id, race_info),
        "file": file
    }

def racetrack_confirm_back_screen(user_id, race_info):
    content = None
    embed = discord.Embed(
        title=f"Are you sure you want to leave the race?",
        description="You will not get your entry fee back",
        color=discord.Color.orange()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")

    return {
        "content": content,
        "embed": embed,
        "view": get_confirm_back_view(user_id, race_info)
    }

def racetrack_horse_select_screen(user_id, race_info):
    horses = db.get_user_horses(user_id)

    return {
        "content": "",  # or a summary string if you'd like
        "embed": None,
        "view": get_racetrack_horse_select_view(user_id, horses, race_info)
    }

def racetrack_results_screen(user_id, race_info, race_results):
    did_win = race_results['winner_id'] == race_info['horse']['id']
    caliber_info = race_info['caliber_info']

    content = None
    embed = discord.Embed(
        color=discord.Color.orange()
    )
    if did_win:
        embed.title=f"Congrats, you won the {caliber_info['name']} race"
        embed.description=f"You have won ${caliber_info['reward']}"
        embed.color=discord.Color.green()
    else:
        embed.title=f"You lost the {caliber_info['name']} race"
        embed.description=f"Better luck next time"
        embed.color=discord.Color.red()

    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    
    return {
        "content": content,
        "embed": embed,
        "view": get_racetrack_results_view(user_id)
    }

def racetrack_custom_race_screen(user_id, custom_race_info):
    track = custom_race_info['track']
    horse1 = custom_race_info['horse1']
    horse2 = custom_race_info['horse2']
    horse3 = custom_race_info['horse3']

    embeds = []
    files = []

    content = None
    main_embed = discord.Embed(
        title=f"Custom Race",
        description="Please select a track and 3 horses",
        color=discord.Color.orange()
    )
    main_embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    main_embed.set_footer(text="Public races allow everyone to see the race and bet on it")

    embeds.append(main_embed)

    track_embed = discord.Embed()
    if not track:
        #no track selected
        track_embed.title=f"Track - ---"
        track_embed.add_field(name="Length", value="---")
        track_embed.add_field(name="", value="")
        track_embed.add_field(name="Tags", value="---")
    else:
        track_embed.title=f"Track - {track['name']}"
        track_embed.add_field(name="Length", value=track['length'])
        track_embed.add_field(name="", value="")
        track_embed.add_field(name="Tags", value=db.get_track_tags_as_string(track))
        
    embeds.append(track_embed)

    horse1_embed = discord.Embed()
    if not horse1:
        horse1_embed.title=f"Horse #1 - ---"
        horse1_embed.add_field(name=f"Speed", value="---")
        horse1_embed.add_field(name=f"Stamina", value="---")
        horse1_embed.add_field(name=f"Agility", value="---")
        horse1_embed.add_field(name=f"Total Stats", value="---")
    else:
        # Extract filename from the stored image_url path
        filename1 = os.path.basename(horse1["image_url"])
        
        if filename1 and os.path.exists(horse1["image_url"]):
            file1 = discord.File(horse1["image_url"], filename=filename1)
        else:
            file1 = discord.File(db.default_horse_image_path(), filename=filename1)

        files.append(file1)
        horse1_embed.set_thumbnail(url=f"attachment://{filename1}")
        horse1_embed.title=f"Horse #1 - {horse1['name']}"
        horse1_embed.add_field(name=f"Speed", value=horse1['speed'])
        horse1_embed.add_field(name=f"Stamina", value=horse1['stamina'])
        horse1_embed.add_field(name=f"Agility", value=horse1['agility'])
        horse1_embed.add_field(name=f"Total Stats", value=(horse1['agility'] + horse1['stamina'] + horse1['speed']))

    embeds.append(horse1_embed)

    horse2_embed = discord.Embed()
    if not horse2:
        horse2_embed.title=f"Horse #2 - ---"
        horse2_embed.add_field(name=f"Speed", value="---")
        horse2_embed.add_field(name=f"Stamina", value="---")
        horse2_embed.add_field(name=f"Agility", value="---")
        horse2_embed.add_field(name=f"Total Stats", value="---")
    else:
        # Extract filename from the stored image_url path
        filename2 = os.path.basename(horse2["image_url"])
        
        if filename2 and os.path.exists(horse2["image_url"]):
            file2 = discord.File(horse2["image_url"], filename=filename2)
        else:
            file2 = discord.File(db.default_horse_image_path(), filename=filename2)

        files.append(file2)
        horse2_embed.set_thumbnail(url=f"attachment://{filename2}")
        horse2_embed.title=f"Horse #1 - {horse2['name']}"
        horse2_embed.add_field(name=f"Speed", value=horse2['speed'])
        horse2_embed.add_field(name=f"Stamina", value=horse2['stamina'])
        horse2_embed.add_field(name=f"Agility", value=horse2['agility'])
        horse2_embed.add_field(name=f"Total Stats", value=(horse2['agility'] + horse2['stamina'] + horse2['speed']))

    embeds.append(horse2_embed)

    horse3_embed = discord.Embed()
    if not horse3:
        horse3_embed.title=f"Horse #3 - ---"
        horse3_embed.add_field(name=f"Speed", value="---")
        horse3_embed.add_field(name=f"Stamina", value="---")
        horse3_embed.add_field(name=f"Agility", value="---")
        horse3_embed.add_field(name=f"Total Stats", value="---")
    else:
        # Extract filename from the stored image_url path
        filename3 = os.path.basename(horse3["image_url"])
        
        if filename3 and os.path.exists(horse3["image_url"]):
            file3 = discord.File(horse3["image_url"], filename=filename3)
        else:
            file3 = discord.File(db.default_horse_image_path(), filename=filename3)

        files.append(file3)
        horse3_embed.set_thumbnail(url=f"attachment://{filename3}")
        horse3_embed.title=f"Horse #1 - {horse3['name']}"
        horse3_embed.add_field(name=f"Speed", value=horse3['speed'])
        horse3_embed.add_field(name=f"Stamina", value=horse3['stamina'])
        horse3_embed.add_field(name=f"Agility", value=horse3['agility'])
        horse3_embed.add_field(name=f"Total Stats", value=(horse3['agility'] + horse3['stamina'] + horse3['speed']))

    embeds.append(horse3_embed)



    return {
        "content": content,
        "view": get_racetrack_custom_race_view(user_id, custom_race_info),
        "embeds": embeds,
        "files": files
    }

def racetrack_custom_track_select_screen(user_id, custom_race_info):
    tracks = db.load_tracks()

    return {
        "content": "",  # or a summary string if you'd like
        "embed": None,
        "view": get_racetrack_custom_track_select_view(user_id, tracks, custom_race_info)
    }

async def racetrack_custom_user_select_screen(user_id, custom_race_info, custom_horse_id):
    users = db.load_users()

    # Filter to users who have at least one public horse
    users_with_public_horses = [
        user_id for user_id in users
        if db.get_user_public_horses(user_id)
    ]

    view = await get_racetrack_custom_user_select_view(
        user_id,
        users_with_public_horses,
        custom_race_info,
        custom_horse_id
    )

    return {
        "content": "",  # or a summary string if you'd like
        "embed": None,
        "view": view
    }

def racetrack_custom_horse_select_screen(user_id, custom_user_id, custom_race_info, custom_horse_id):
    horses = db.get_user_public_horses(custom_user_id)

    return {
        "content": "",  # or a summary string if you'd like
        "embed": None,
        "view": get_racetrack_custom_horse_select_view(user_id, horses, custom_race_info, custom_horse_id)
    }

def racetrack_custom_race_results_screen(user_id, is_ephemeral, race_results, bets, odds):
    winning_horse = db.get_horse_by_id(race_results['winner_id'])
    results = [f"🎉 **{winning_horse['name']}** wins the race!\n"]

    total_house_cut = 0

    if not bets:
        results.append("⏹️ No one placed a bet.")

    for user_id, bet in bets.items():
        horse_id = bet["horse_id"]
        amount = bet["amount"]
        if horse_id == race_results['winner_id']:
            payout = round(amount * odds[horse_id]["decimal_odds"])
            db.update_balance(user_id, payout)
            results.append(f"<@{user_id}> won ${payout}! 🤑")
            total_house_cut += round(amount * odds[horse_id]["house_payout"])
        else:
            db.update_balance(user_id, -amount)
            results.append(f"<@{user_id}> lost ${amount}. 💸")
            total_house_cut += amount

    

    content = ("\n".join(results))
    
    return {
        "content": content,
        "embed": None,
        "view": get_racetrack_custom_race_results_view(user_id, is_ephemeral)
    }
