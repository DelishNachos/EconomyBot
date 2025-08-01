import discord
from discord.ext import commands
import json
import os

class UserHorses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.horses_file = "data/horses.json"  # Adjust path

    def get_user_horses(self, user_id):
        with open(self.horses_file, "r") as f:
            all_horses = json.load(f)
        # Filter horses owned by user_id (string)
        return [h for h in all_horses if h.get("owner") == str(user_id)]

    @discord.slash_command(name="myhorses", description="List all your horses")
    async def myhorses(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.author.id)
        horses = self.get_user_horses(user_id)

        if not horses:
            await ctx.respond("You don't own any horses yet.")
            return

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Horses",
            color=discord.Color.blurple()
        )

        for horse in horses:
            name = horse.get("name", "Unknown")
            speed = horse.get("speed", 0)
            stamina = horse.get("stamina", 0)
            agility = horse.get("agility", 0)
            energy = horse.get("energy", "N/A")
            wins = horse.get("wins", 0)
            races = horse.get("races", 0)
            public = horse.get("public", False)

            stats_text = (
                f"**Stats:** Speed: {speed}, Stamina: {stamina}, Agility: {agility}\n"
                f"**Energy:** {energy}\n"
                f"🏆 Wins: {wins} | 🐎 Races: {races}\n"
                f"**Public:** {public}"
                "------------------------------------------------------------------"
            )
            embed.add_field(name=name, value=stats_text, inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(UserHorses(bot))