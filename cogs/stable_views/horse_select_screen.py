import discord

from cogs.stable_views import stable_view_factory
from utils import db

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horses_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class HorseSelectView(discord.ui.View):
    def __init__(self, user_id, horses):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(HorseDropdown(user_id, horses))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class HorseDropdown(discord.ui.Select):
    def __init__(self, user_id, horses):
        options = [
            discord.SelectOption(label=f"{horse['name']}: {horse['speed']}, {horse['stamina']}, {horse['agility']}", value=horse['id'])
            for horse in horses
        ]
        super().__init__(placeholder="Choose a horse...", options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        horse_id = self.values[0]
        response = stable_view_factory.horse_manage_screen(self.user_id, db.get_horse_by_id(horse_id))

        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )