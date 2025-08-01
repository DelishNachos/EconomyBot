import discord

from cogs.stable_views import stable_view_factory
from utils import db


class BackButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_manage_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )

class ItemGiveView(discord.ui.View):
    def __init__(self, user_id, horse, item):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.horse = horse

        can_use = db.get_user_item_count(user_id, item) > 0

        self.add_item(GiveButton(horse, item, can_use))
        self.add_item(BackButton(horse))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class GiveButton(discord.ui.Button):
    def __init__(self, horse, item, can_use):
        super().__init__(label="Give", style=discord.ButtonStyle.primary)
        self.horse = horse
        self.item = item
        if not can_use:
            self.disabled = True


    async def callback(self, interaction: discord.Interaction):
        db.use_item(interaction.user.id, self.horse, self.item)

        response = stable_view_factory.item_give_screen(interaction.user.id, self.horse, self.item)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )