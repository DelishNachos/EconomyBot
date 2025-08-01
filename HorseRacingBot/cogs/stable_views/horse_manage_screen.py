import asyncio
import os
import discord

from cogs.stable_views import stable_view_factory
from utils import db
from utils.image_validator import validate_image


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horses_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class HorseManageView(discord.ui.View):
    def __init__(self, user_id, horse):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.horse = horse

        self.add_item(TrainButton(horse))
        self.add_item(GiveItemButton(horse))
        self.add_item(CustomizeButton(horse))
        self.add_item(TogglePublicButton(horse))
        self.add_item(RetireButton(horse))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    

class TrainButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Train", style=discord.ButtonStyle.primary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_training_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response["file"]
        )


class GiveItemButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Give Item", style=discord.ButtonStyle.primary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.item_select_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class CustomizeButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Customize", style=discord.ButtonStyle.primary)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_customize_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response["file"]
        )
            

class TogglePublicButton(discord.ui.Button):
    def __init__(self, horse):
        self.horse = horse
        label = "Public: ON" if horse.get("public", False) else "Public: OFF"
        style = discord.ButtonStyle.success if horse.get("public", False) else discord.ButtonStyle.danger
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        if self.horse:
            self.horse["public"] = not self.horse.get("public", False)
            db.update_horse(self.horse)

            response = stable_view_factory.horse_manage_screen(interaction.user.id, self.horse)
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                file=response['file']
            )
            # Update button appearance
            # new_view = ManageHorseView(horse)
            # await interaction.response.edit_message(content=f"🐴 Managing **{horse['name']}**", view=new_view)
        else:
            await interaction.response.send_message("❌ Horse not found.", ephemeral=True)

class RetireButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label="Retire Horse", style=discord.ButtonStyle.danger)
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        response = stable_view_factory.horse_retire_confirm_screen(interaction.user.id, self.horse)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )