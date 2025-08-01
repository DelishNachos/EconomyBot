import discord

from cogs.shop_views import shop_view_factory
from utils import db


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = shop_view_factory.shop_items_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class ShopItemTypeView(discord.ui.View):
    def __init__(self, user_id, item_type):
        super().__init__(timeout=300)
        self.user_id = user_id
        items = db.get_items_by_type(item_type)
        for item in items:
            self.add_item(BuyButton(item, db.can_buy_item(user_id, item)))

        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class BuyButton(discord.ui.Button):
    def __init__(self, item, can_buy):
        super().__init__(label=f"Buy {item['name']}", style=discord.ButtonStyle.success)
        self.item = item
        if not can_buy:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        if not db.can_buy_item(interaction.user.id, self.item):
            self.disabled = True
            response = shop_view_factory.shop_item_type_screen(interaction.user.id, self.item['type'])
            content = f"You do not have enough money to purchase {self.item['name']}"

            await interaction.response.edit_message(
                content=content,
                view=response["view"],
                embeds=response['embeds']
            )
            return

        db.buy_item(interaction.user.id, self.item)

        response = shop_view_factory.shop_item_type_screen(interaction.user.id, self.item['type'])
        await interaction.response.edit_message(
            content=f"Successfully bought 1 {self.item['name']}",
            embeds=response["embeds"],
            view=response["view"]
        )