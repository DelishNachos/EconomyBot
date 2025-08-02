from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import os
from utils import db

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.table_name = os.getenv("DYNAMODB_TABLE_NAME")

    @discord.slash_command(guild_ids=[int(os.getenv("DISCORD_GUILD_ID"))])
    async def balance(self, ctx):
        user_id = str(ctx.author.id)
        balance = db.get_balance(user_id)
        await ctx.respond(f"💸 You have ${balance}.", ephemeral=True)

    @discord.slash_command(guild_ids=[int(os.getenv("DISCORD_GUILD_ID"))])
    async def daily(self, ctx):
        daily_amount = db.get_general_config()['daily_amount']

        user_id = str(ctx.author.id)
        user = db.get_user(user_id)

        now = datetime.now(timezone.utc)
        last_claimed_str = user.get("last_daily")

        if last_claimed_str:
            last_claimed = datetime.strptime(last_claimed_str, "%Y-%m-%dT%H:%M:%S")
            next_claim_time = last_claimed + timedelta(days=1)

            if now < next_claim_time:
                time_remaining = next_claim_time - now
                hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                await ctx.respond(
                    f"⏳ You’ve already claimed your daily reward today!\n"
                    f"Come back in **{hours}h {minutes}m {seconds}s**.",
                    ephemeral=True
                )
                return

        # Give reward
        user["last_daily"] = now.strftime("%Y-%m-%dT%H:%M:%S")
        db.update_user(user)
        db.update_balance(user_id, daily_amount)

        balance = db.get_balance(user_id)
        await ctx.respond(f"✅ You claimed ${daily_amount}! Your new balance is ${balance}.", ephemeral=True)

    @discord.slash_command(name="send_money", description="Send money to another user")
    async def send_money(self, ctx: discord.ApplicationContext, user: discord.User):
        if user.id == ctx.user.id:
            await ctx.respond("❌ You can't send money to yourself.", ephemeral=True)
            return

        modal = SendMoneyModal(sender=ctx.user, recipient=user)
        await ctx.send_modal(modal)

    
class SendMoneyModal(discord.ui.Modal):
    def __init__(self, sender: discord.User, recipient: discord.User):
        super().__init__(title="Send Money")
        self.sender = sender
        self.recipient = recipient

        self.amount_input = discord.ui.InputText(
            label="Amount to Send",
            placeholder="Enter amount (e.g., 100)",
            required=True,
        )
        self.add_item(self.amount_input)

    async def callback(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)

            if amount <= 0:
                await interaction.response.send_message("🚫 Amount must be greater than zero.", ephemeral=True)
                return

            # Example balance check (replace with real logic)
            sender_balance = db.get_balance(self.sender.id)
            if sender_balance < amount:
                await interaction.response.send_message("❌ You don't have enough money!", ephemeral=True)
                return

            # Update balances
            db.update_balance(self.sender.id, -amount)
            db.update_balance(self.recipient.id, amount)

            await interaction.response.send_message(
                f"💸 {self.sender.mention} sent {amount} coins to {self.recipient.mention}!",
                ephemeral=False
            )

        except ValueError:
            await interaction.response.send_message("❌ Invalid number entered.", ephemeral=True)



def setup(bot):
    bot.add_cog(Economy(bot))