import discord

from cogs.shop_views import shop_view_factory


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = shop_view_factory.main_shop_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class ShopItemView(discord.ui.View):
    def __init__(self, user_id, item_types):
        super().__init__(timeout=300)
        self.user_id = user_id
        for item in item_types:
            self.add_item(ItemTypeButton(item))

        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class ItemTypeButton(discord.ui.Button):
    def __init__(self, item_type):
        super().__init__(label=item_type, style=discord.ButtonStyle.primary)
        self.item_type = item_type

    async def callback(self, interaction: discord.Interaction):
        response = shop_view_factory.shop_item_type_screen(interaction.user.id, self.item_type)
        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"]
        )
