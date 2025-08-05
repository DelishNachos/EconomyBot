import asyncio
import discord

from cogs.stable_views import stable_view_factory
from utils import db
from utils.image_validator import validate_image

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

class HorseCustomizeView(discord.ui.View):
    def __init__(self, user_id, horse):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.horse = horse

        self.add_item(ChangeNameButton(self.horse))
        self.add_item(ChangeImageButton(self.horse))
        self.add_item(BackButton(self.horse))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    

class ChangeNameButton(discord.ui.Button):
    def __init__(self, horse):
        self.horse = horse
        super().__init__(label="Change Name", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        modal = ChangeNameModal(self.horse, interaction)
        await interaction.response.send_modal(modal)


class ChangeNameModal(discord.ui.Modal):
    def __init__(self, horse, interaction: discord.Interaction):
        super().__init__(title="Change Horse Name")
        self.horse = horse

        self.name_input = discord.ui.InputText(
            label="New Horse Name",
            placeholder="New Name (Max length 18 including spaces)",
            max_length=18
        )
        self.add_item(self.name_input)

    async def callback(self, interaction: discord.Interaction):
        new_name = self.name_input.value.strip()

        if not new_name:
            # Generate updated response content
            response = stable_view_factory.horse_customize_screen(interaction.user.id, self.horse)
            await interaction.response.edit_message(
                content=f"Failed to change name. Name cannot be empty",
                embed=response["embed"],
                file=response['file'],
                view=response["view"]
            )
            return

        old_name = self.horse['name']
        self.horse["name"] = new_name
        db.update_horse(self.horse)

        # Generate updated response content
        response = stable_view_factory.horse_customize_screen(interaction.user.id, self.horse)

        await interaction.response.edit_message(
            content=f"Successfully changed name from **{old_name}** to **{new_name}**",
            embed=response["embed"],
            file=response['file'],
            view=response["view"]
        )

class ChangeImageButton(discord.ui.Button):
    def __init__(self, horse):
        self.horse = horse
        super().__init__(label="Change Image", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Please upload an image file (max 200KB, 256x256 pixels) for your horse. Type `cancel` to stop.",
            ephemeral=True
        )

        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        while True:
            try:
                msg = await interaction.client.wait_for("message", check=check, timeout=60)

                # Allow user to cancel
                if msg.content.strip().lower() == "cancel":
                    await interaction.followup.send("Image update canceled.", ephemeral=True)
                    response = stable_view_factory.horse_customize_screen(interaction.user.id, self.horse)

                    # Send updated message
                    await interaction.followup.send(
                        content=response['content'],
                        embed=response["embed"],
                        file=response['file'],
                        ephemeral=True,
                        view=response["view"]
                    )
                    return

                # Make sure the message has an attachment
                if not msg.attachments:
                    await interaction.followup.send("Please attach an image file.", ephemeral=True)
                    continue

                attachment = msg.attachments[0]

                # Validate file size and dimensions
                valid, message = await validate_image(attachment)
                if not valid:
                    await interaction.followup.send(message + " Please try again or type `cancel` to exit.", ephemeral=True)
                    continue

                # Valid image, save it
                file_ext = attachment.filename.split('.')[-1].lower()
                if file_ext not in ["png", "jpg", "jpeg", "gif"]:
                    file_ext = "png"

                file_path = f"{db.ASSETS_PATH}/horses/{self.horse['id']}.{file_ext}"
                await attachment.save(file_path)

                # Update horse data
                self.horse["image_url"] = file_path
                db.update_horse(self.horse)

                # Create response
                response = stable_view_factory.horse_customize_screen(interaction.user.id, self.horse)
                file = discord.File(file_path, filename=f"{self.horse['id']}.{file_ext}")

                # Send updated message
                await interaction.followup.send(
                    content="Horse image updated successfully!",
                    embed=response["embed"],
                    file=file,
                    ephemeral=True,
                    view=response["view"]
                )
                return  # Exit loop after success

            except asyncio.TimeoutError:
                await interaction.followup.send("Image upload timed out. Please try again later.", ephemeral=True)
                return