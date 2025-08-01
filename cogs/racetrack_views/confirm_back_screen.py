import discord

from cogs.racetrack_views import racetrack_view_factory


class ConfirmLeaveView(discord.ui.View):
    def __init__(self, user_id, race_info):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(ConfirmButton())
        self.add_item(CancelButton(race_info))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class ConfirmButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Confirm", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_heat_select_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class CancelButton(discord.ui.Button):
    def __init__(self, race_info):
        super().__init__(label="Cancel", style=discord.ButtonStyle.secondary)
        self.race_info = race_info

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_pre_race_screen(interaction.user.id, self.race_info)
        if not self.race_info['horse']:
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                attachments=response["attachments"]
            )
        else:
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                file=response["file"]
            )