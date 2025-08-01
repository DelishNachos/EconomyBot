import discord

from cogs.stable_views import stable_view_factory

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

class HorseTrainingView(discord.ui.View):
    def __init__(self, user_id, horse):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.horse = horse

        self.add_item(SpeedButton(horse))
        self.add_item(StaminaButton(horse))
        self.add_item(AgilityButton(horse))
        self.add_item(BackButton(horse))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class SpeedButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Speed", style=discord.ButtonStyle.primary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.speed_training_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )   

class StaminaButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Stamina", style=discord.ButtonStyle.primary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.stamina_training_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )   

class AgilityButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Agility", style=discord.ButtonStyle.primary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.agility_training_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )   