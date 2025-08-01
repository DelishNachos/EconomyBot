import discord

from cogs.stable_views import stable_view_factory
from utils import db, training_calculator


class BackButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_training_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )

class SpeedTrainingView(discord.ui.View):
    def __init__(self, user_id, horse):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.horse = horse

        can_buy = db.get_balance(user_id) >= training_calculator.calculate_cost(horse['speed'])

        self.add_item(StartButton(horse, can_buy))
        self.add_item(BackButton(horse))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class StartButton(discord.ui.Button):
    def __init__(self, horse, can_buy):
        super().__init__(label="Start", style=discord.ButtonStyle.primary)
        self.horse = horse
        if not can_buy:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        response = await stable_view_factory.speed_game_screen(interaction, interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )