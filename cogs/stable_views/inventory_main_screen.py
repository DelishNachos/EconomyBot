import discord
from cogs.stable_views import stable_view_factory
from utils import db

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

class InventoryMainView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        sorted_item_types = sorted(db.get_user_item_types(user_id))
        for item_type in sorted_item_types:
            self.add_item(TypeButton(item_type))

        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class TypeButton(discord.ui.Button):
    def __init__(self, item_type):
        super().__init__(label=item_type, style=discord.ButtonStyle.primary)
        self.item_type = item_type

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.inventory_type_screen(interaction.user.id, self.item_type)
        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"]
        )