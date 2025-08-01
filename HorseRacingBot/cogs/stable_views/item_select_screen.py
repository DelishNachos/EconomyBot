import discord

from cogs.stable_views import stable_view_factory
from utils import db

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

class ItemSelectView(discord.ui.View):
    def __init__(self, user_id, horse, items):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(ItemDropdown(user_id, horse, items))
        self.add_item(BackButton(horse))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class ItemDropdown(discord.ui.Select):
    def __init__(self, user_id, horse, items):
        options = [
            discord.SelectOption(label=f"{item['name']} (X{db.get_user_item_count(user_id, item)}): Energy - {item['energy']}%", value=item['id'])
            for item in items
        ]
        super().__init__(placeholder="Choose an item...", options=options)
        self.user_id = user_id
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        item_id = self.values[0]
        print(item_id)
        response = stable_view_factory.item_give_screen(self.user_id, self.horse, db.get_item_by_id(item_id))

        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )