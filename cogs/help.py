from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import os
from utils import db

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="Link to the help guide", guild_ids=[int(id) for id in os.getenv("DISCORD_GUILD_ID").split(",")])
    async def balance(self, ctx):
        embed = discord.Embed(
            title="📘 Horse Racing Bot Help",
            description="Click the link below to view the help guide:",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="Documentation",
            value="[View Help Document](https://docs.google.com/document/d/1jB-vo6wACGcU9yJP98AXwwDHtza4ScIe5QiHTBH8mtk/edit?usp=sharing)",
            inline=False
        )
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Help(bot))