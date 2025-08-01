import discord
from discord.ext import commands
from discord.ui import InputText

from utils import db


class HorseRaceView(discord.ui.View):
    def __init__(self, horses, timeout=30):
        super().__init__(timeout=timeout)
        self.bets = {}  # {user_id: {"horse_id": str, "amount": int}}
        self.horses = horses
        self.betting_open = True
        for horse in horses:
            self.add_item(HorseBetButton(horse))

    def close_betting(self):
        self.betting_open = False
        # Disable all buttons to indicate betting is closed
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

class HorseBetButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label=f"{horse['name']} 🐎", style=discord.ButtonStyle.primary, custom_id=horse["id"])
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        view: HorseRaceView = self.view

        if not view.betting_open:
            await interaction.response.send_message("❌ Betting time is over. No more bets allowed.", ephemeral=True)
            return

        # Ask how much they want to bet
        await interaction.response.send_modal(HorseBetModal(self.horse, view, interaction))

class HorseBetModal(discord.ui.Modal):
    def __init__(self, horse, view: HorseRaceView, interaction: discord.Interaction):
        super().__init__(title=f"Bet on {horse['name']} (💰 ${db.get_balance(interaction.user.id)})")
        self.horse = horse
        self.view = view

        self.bet_amount = InputText(
            label="Bet Amount",
            placeholder=f"Your balance: ${db.get_balance(interaction.user.id)}",
            required=True,
        )
        self.add_item(self.bet_amount)

    async def callback(self, interaction: discord.Interaction):
        from utils.db import get_balance  # Avoid circular imports
        user_id = str(interaction.user.id)
        amount = self.bet_amount.value

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ Invalid bet amount.", ephemeral=True)
            return

        balance = get_balance(user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough money for that bet.", ephemeral=True)
            return

        # Save the bet
        self.view.bets[user_id] = {
            "horse_id": self.horse["id"],
            "amount": amount
        }

        await interaction.response.send_message(
            f"✅ You bet **${amount}** on **{self.horse['name']}**!", ephemeral=True
        )

class HorseRacing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.race_in_progress = False
        self.current_race = None

    @discord.slash_command(name="startrace", description="Start a new horse race", guild_ids=[int(os.getenv("DISCORD_GUILD_ID"))])
    async def startrace(self, ctx):