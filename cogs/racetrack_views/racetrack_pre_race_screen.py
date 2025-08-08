import asyncio
import discord

from cogs.racetrack_views import racetrack_view_factory
from utils import db
from utils.race_simulator import simulate_solo_race


class RacetrackPreRaceView(discord.ui.View):
    def __init__(self, user_id, race_info):
        super().__init__(timeout=300)
        self.user_id = user_id

        if not race_info['in_progress']:
            self.add_item(StartRaceButton(race_info))
            self.add_item(SelectHorseButton(race_info))
            self.add_item(PublicButton(race_info))
            self.add_item(LeaveRaceButton(race_info))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class StartRaceButton(discord.ui.Button):
    def __init__(self, race_info):
        super().__init__(label="Start Race", style=discord.ButtonStyle.primary)
        self.race_info = race_info
        if not self.race_info['horse']:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        self.race_info['in_progress'] = True
        is_ephemeral = not self.race_info['public']
        # Step 1: Show the pre-race screen
        response = racetrack_view_factory.racetrack_pre_race_screen(interaction.user.id, self.race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

        # Step 2: Send temporary "Preparing your race..." message
        preparing_message = await interaction.followup.send(
            content=f"⏳ Preparing {self.race_info['caliber_info']['name']} race for {self.race_info['horse']['name']}...",
            ephemeral=is_ephemeral,
            wait=True
        )

        print("Simulating race...")
        # Step 3: Simulate the race
        race_results = simulate_solo_race(self.race_info)
        print("Race simulation complete.")

        # Step 4: Edit the "Preparing..." message to show the race GIF
        gif_file = discord.File(fp=race_results["gif_bytes"], filename="race.gif")
        await preparing_message.edit(
            content="🏇 Here's your race!",
            file=gif_file
        )

        # Step 5: Wait for the race GIF to play
        gif_duration_sec = race_results["gif_duration_ms"] / 1000
        await asyncio.sleep(gif_duration_sec + 1)

        if self.race_info['horse']['id'] == race_results['winner_id']:
            db.update_balance(interaction.user.id, self.race_info['caliber_info']['reward'])

        # Step 6: Send the final race results (ephemeral)
        result_response = racetrack_view_factory.racetrack_results_screen(
            interaction.user.id, self.race_info, race_results
        )
        await interaction.followup.send(
            content=result_response['content'],
            embed=result_response['embed'],
            view=racetrack_view_factory.get_racetrack_results_view(interaction.user.id),
            ephemeral=is_ephemeral
        )

        

class SelectHorseButton(discord.ui.Button):
    def __init__(self, race_info):
        super().__init__(label="Select Horse", style=discord.ButtonStyle.primary)
        self.race_info = race_info

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_horse_select_screen(interaction.user.id, self.race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class PublicButton(discord.ui.Button):
    def __init__(self, race_info):
        self.race_info = race_info
        label = "Public: ON" if race_info['public'] else "Public: OFF"
        style = discord.ButtonStyle.success if race_info['public'] else discord.ButtonStyle.danger
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        current_value = self.race_info["public"]
        self.race_info["public"] = not current_value

        response = racetrack_view_factory.racetrack_pre_race_screen(interaction.user.id, self.race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )



class LeaveRaceButton(discord.ui.Button):
    def __init__(self, race_info):
        super().__init__(label="Leave Race", style=discord.ButtonStyle.red)
        self.race_info = race_info

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_confirm_back_screen(interaction.user.id, self.race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )