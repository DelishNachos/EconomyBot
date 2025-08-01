import discord

from cogs.racetrack_views import racetrack_view_factory

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_main_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class RacetrackHeatSelectView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(HeatButton("H4"))
        self.add_item(HeatButton("H3"))
        self.add_item(HeatButton("H2"))
        self.add_item(HeatButton("H1"))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class HeatButton(discord.ui.Button):
    def __init__(self, caliber):
        super().__init__(label=caliber, style=discord.ButtonStyle.primary)
        self.caliber = caliber

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_heat_info_screen(interaction.user.id, self.caliber)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )