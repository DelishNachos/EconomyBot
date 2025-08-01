import discord
from discord.ext import commands
from cogs.shop_views import shop_view_factory
from utils import db

class ShopManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="shop", description="Shop for horses and items.")
    async def stables(self, ctx: discord.ApplicationContext):
        
        user_id = ctx.author.id
        response = shop_view_factory.main_shop_screen(user_id)
        await ctx.respond(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(ShopManager(bot))