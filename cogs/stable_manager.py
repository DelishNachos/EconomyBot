import discord
from discord.ext import commands
from cogs.stable_views import stable_view_factory
from utils import db

class StableManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="stables", description="Manage your stables.")
    async def stables(self, ctx: discord.ApplicationContext):
        
        user_id = ctx.author.id
        response = stable_view_factory.main_stable_screen(user_id)
        await ctx.respond(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(StableManager(bot))