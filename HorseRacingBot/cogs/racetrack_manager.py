import discord
from discord.ext import commands
from cogs.racetrack_views import racetrack_view_factory
from utils import db

class RacetrackManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="racetrack", description="Visit the racetrack to race your horses.")
    async def stables(self, ctx: discord.ApplicationContext):
        
        user_id = ctx.author.id
        response = racetrack_view_factory.racetrack_main_screen(user_id)
        await ctx.respond(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(RacetrackManager(bot))