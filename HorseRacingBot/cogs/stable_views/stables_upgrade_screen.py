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

class UpgradeScreenView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        next_level_data = db.get_stable_level_data(db.get_stable_data(user_id)['level'] + 1)
        can_buy = db.get_balance(user_id) >= next_level_data['cost']

        self.add_item(UpgradeButton(can_buy))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class UpgradeButton(discord.ui.Button):
    def __init__(self, can_buy):
        super().__init__(label="Buy Upgrade", style=discord.ButtonStyle.success)
        if not can_buy:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        if not db.can_upgrade_stable(interaction.user.id):
            # Disable the button and re-render the view to reflect it
            self.disabled = True
            response = stable_view_factory.stables_upgrade_screen(interaction.user.id)
            response["view"].children[0].disabled = True  # You can also do this if needed
            await interaction.response.edit_message(
                content="You don't have enough money to upgrade.",
                view=response["view"]
            )
            return  # Exit early

        # Perform the upgrade
        db.upgrade_stable_data(interaction.user.id)

        # Refresh the UI after upgrading
        response = stable_view_factory.stables_upgrade_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )