import discord
from cogs.racetrack_views import racetrack_view_factory
from utils import db


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_heat_select_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class RacetrackHeatInfoView(discord.ui.View):
    def __init__(self, user_id, caliber):
        super().__init__(timeout=300)
        self.user_id = user_id

        caliber_info =  db.get_horse_racing_caliber_info_by_caliber(caliber)
        can_buy = db.get_balance(user_id) >= caliber_info['cost']

        self.add_item(EnterButton(caliber_info, can_buy))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class EnterButton(discord.ui.Button):
    def __init__(self, caliber_info, can_buy):
        super().__init__(label=f"Enter-${caliber_info['cost']}", style=discord.ButtonStyle.success)
        self.caliber_info = caliber_info
        if not can_buy:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        race_info = {
            "horse": None,
            "track": db.get_random_race_track(),
            "caliber_info": self.caliber_info,
            "in_progress": False
        }

        db.update_balance(interaction.user.id, -self.caliber_info['cost'])

        response = racetrack_view_factory.racetrack_pre_race_screen(interaction.user.id, race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )