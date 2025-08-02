import discord
from cogs.stable_views import stable_view_factory

class MainStableView(discord.ui.View):
    def __init__(self, user_id, stable_data):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.stable_data = stable_data

        self.add_item(HorsesButton())
        self.add_item(InventoryButton())
        self.add_item(ManageStableButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class HorsesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Horses", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horses_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class InventoryButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Inventory", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.inventory_main_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class ManageStableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Manage Stable", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.stables_manage_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )