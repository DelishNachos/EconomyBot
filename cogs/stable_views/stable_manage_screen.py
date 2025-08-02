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

class StableManageView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(RenameButton())
        self.add_item(UpgradeButton())
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class RenameButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Rename", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        modal = ChangeNameModal(interaction)
        await interaction.response.send_modal(modal)

class UpgradeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Upgrade", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.stables_upgrade_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"]
        )

class ChangeNameModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(title="Change Stable Name")

        self.name_input = discord.ui.InputText(
            label="New Stable Name",
            placeholder="Enter the new name for your stable",
            max_length=50
        )
        self.add_item(self.name_input)

    async def callback(self, interaction: discord.Interaction):
        new_name = self.name_input.value.strip()

        if not new_name:
            # Generate updated response content
            response = stable_view_factory.stables_manage_screen(interaction.user.id)
            await interaction.response.edit_message(
                content=f"Failed to change name. Name cannot be empty",
                embed=response["embed"],
                view=response["view"]
            )
            return

        user_data = db.get_user(interaction.user.id)
        old_name = user_data['stables']['name']
        user_data['stables']['name'] = new_name
        db.update_user(user_data)

        # Generate updated response content
        response = stable_view_factory.stables_manage_screen(interaction.user.id)

        await interaction.response.edit_message(
            content=f"Successfully changed name from **{old_name}** to **{new_name}**",
            embed=response["embed"],
            view=response["view"]
        )