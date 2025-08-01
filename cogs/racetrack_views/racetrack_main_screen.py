import discord

from cogs.racetrack_views import racetrack_view_factory


class RacetrackMainView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(HeatSelectButton())
        self.add_item(CustomRaceButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class HeatSelectButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Enter Race", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_heat_select_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class CustomRaceButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Custom Race", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        custom_race_info = {
            "track": None,
            "horse1": None,
            "horse2": None,
            "horse3": None,
            "public": False
        }

        response = racetrack_view_factory.racetrack_custom_race_screen(interaction.user.id, custom_race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"],
            files=response['files']
        )