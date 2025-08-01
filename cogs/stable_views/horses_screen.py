import discord
from cogs.stable_views import stable_view_factory

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.main_stable_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class HorsesScreenView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(HorseManageButton())
        self.add_item(HorseListButton())
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class HorseListButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Horse List", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_list_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class HorseManageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Manage Horses", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_select_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )