import discord
from cogs.shop_views import shop_view_factory

class MainShopView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(HorseShopButton())
        self.add_item(ItemShopButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class HorseShopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Horses", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = shop_view_factory.shop_horses_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"]
        )

class ItemShopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Items", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        response = shop_view_factory.shop_items_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )