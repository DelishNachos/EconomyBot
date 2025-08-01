import discord

from cogs.stable_views import stable_view_factory
from utils import db


class ConfirmRetireView(discord.ui.View):
    def __init__(self, user_id, horse):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(ConfirmButton(horse))
        self.add_item(CancelButton(horse))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class ConfirmButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Confirm", style=discord.ButtonStyle.red)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        db.remove_horse_from_user(interaction.user.id, self.horse)
        response = stable_view_factory.horses_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class CancelButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Cancel", style=discord.ButtonStyle.secondary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_manage_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                file=response["file"]
            )