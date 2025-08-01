import discord

from cogs.racetrack_views import racetrack_view_factory


class BackButton(discord.ui.Button):
    def __init__(self, is_ephemeral):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.is_ephemeral = is_ephemeral

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_main_screen(interaction.user.id)
        if self.is_ephemeral:
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
            )
        else:
            await interaction.response.send_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                ephemeral=True
            )

        

class RacetrackCustomResultsView(discord.ui.View):
    def __init__(self, user_id, is_ephemeral):
        super().__init__(timeout=300)
        self.user_id = user_id

        #self.add_item(BackButton(is_ephemeral))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id