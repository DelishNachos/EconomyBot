import discord
from discord.ext import commands

from cogs.bank_views import bank_view_factory

class BankManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="bank", description="Go to the bank.")
    async def bank(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id
        response = bank_view_factory.bank_main_screen(user_id)
        await ctx.respond(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(BankManager(bot))