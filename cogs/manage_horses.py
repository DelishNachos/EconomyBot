import discord
import json
from discord.ext import commands
from pathlib import Path

HORSES_PATH = Path("data/horses.json")

def load_horses():
    if not HORSES_PATH.exists():
        return []
    with open(HORSES_PATH) as f:
        return json.load(f)

def save_horses(horses):
    with open(HORSES_PATH, "w") as f:
        json.dump(horses, f, indent=2)

class RenameModal(discord.ui.Modal):
    def __init__(self, horse_id):
        super().__init__(title="Rename Horse")
        self.horse_id = horse_id
        self.new_name = discord.ui.InputText(label="New Name", max_length=32)
        self.add_item(self.new_name)

    async def callback(self, interaction: discord.Interaction):
        horses = load_horses()
        horse = next((h for h in horses if h["id"] == self.horse_id), None)

        if horse:
            old_name = horse["name"]
            horse["name"] = self.new_name.value
            save_horses(horses)
            await interaction.response.send_message(
                f"✅ Renamed **{old_name}** to **{horse['name']}**!", ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Horse not found.", ephemeral=True)

class ManageHorseView(discord.ui.View):
    def __init__(self, horse):
        super().__init__(timeout=60)
        self.horse = horse
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        self.add_item(RenameHorseButton(self.horse["id"]))
        self.add_item(TogglePublicButton(self.horse))

class RenameHorseButton(discord.ui.Button):
    def __init__(self, horse_id):
        super().__init__(label="Rename", style=discord.ButtonStyle.blurple)
        self.horse_id = horse_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RenameModal(self.horse_id))

class TogglePublicButton(discord.ui.Button):
    def __init__(self, horse):
        self.horse = horse
        label = "Public: ON" if horse.get("public", False) else "Public: OFF"
        style = discord.ButtonStyle.success if horse.get("public", False) else discord.ButtonStyle.danger
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        horses = load_horses()
        horse = next((h for h in horses if h["id"] == self.horse["id"]), None)

        if horse:
            horse["public"] = not horse.get("public", False)
            save_horses(horses)

            # Update button appearance
            new_view = ManageHorseView(horse)
            await interaction.response.edit_message(content=f"🐴 Managing **{horse['name']}**", view=new_view)
        else:
            await interaction.response.send_message("❌ Horse not found.", ephemeral=True)

class HorseDropdown(discord.ui.Select):
    def __init__(self, horses):
        options = [
            discord.SelectOption(label=horse["name"], value=horse["id"])
            for horse in horses
        ]
        super().__init__(placeholder="Select a horse to manage", options=options)

    async def callback(self, interaction: discord.Interaction):
        horses = load_horses()
        horse = next((h for h in horses if h["id"] == self.values[0]), None)
        if horse:
            await interaction.response.edit_message(
                content=f"🐴 Managing **{horse['name']}**",
                view=ManageHorseView(horse)
            )
        else:
            await interaction.response.send_message("❌ Horse not found.", ephemeral=True)

class HorseDropdownView(discord.ui.View):
    def __init__(self, horses):
        super().__init__(timeout=60)
        self.add_item(HorseDropdown(horses))

class HorseManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="manage_horses", description="Manage your horses")
    async def horse_manage(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.user.id)
        horses = load_horses()
        user_horses = [h for h in horses if h.get("owner") == user_id]

        if not user_horses:
            await ctx.respond("😢 You don't own any horses.", ephemeral=True)
            return

        await ctx.respond("Select a horse to manage:", view=HorseDropdownView(user_horses), ephemeral=True)

def setup(bot):
    bot.add_cog(HorseManagement(bot))