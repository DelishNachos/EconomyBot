import discord
from cogs.shop_views import shop_view_factory
from utils import db

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

class ShopHorsesView(discord.ui.View):
    def __init__(self, user_id, horses):
        super().__init__(timeout=300)
        self.user_id = user_id
        for i, horse in enumerate(horses):
            can_buy, reason = db.can_buy_horse(user_id, horse)
            self.add_item(BuyHorseButton(label=f"Buy Horse #{i+1}", horse=horse, can_buy=can_buy))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class BuyHorseButton(discord.ui.Button):
    def __init__(self, label, horse, can_buy):
        super().__init__(label=label, style=discord.ButtonStyle.green)
        self.horse = horse
        if not can_buy:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        # if not can_buy:
        #     self.disabled = True
        #     response = shop_view_factory.shop_horses_screen(interaction.user.id)
            
        #     if reason == "balance":
        #         content = "You don't have enough money for that horse."
        #     elif reason == "max_horses":
        #         content = "You don't have enough space for that horse"
        #     else:
        #         content = "Something went wrong"

        #     await interaction.response.edit_message(
        #         content=content,
        #         view=response["view"]
        #     )
        #     return
        
        db.buy_horse(interaction.user.id, self.horse)

        response = shop_view_factory.shop_horses_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"]
        )