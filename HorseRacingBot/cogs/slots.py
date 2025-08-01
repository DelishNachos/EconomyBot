import discord
import random
import asyncio
from discord.ext import commands
from utils.image_generator import generate_slot_gif

SLOT_SYMBOLS = ["🍒", "🍋", "🔔", "⭐", "🍇", "💎", "7️⃣"]

class SlotMachineView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.message = None
        self.grid = [["❓"]*3 for _ in range(3)]

    def render_grid(self):
        lines = []
        for row in self.grid:
            lines.append(" ".join(row))
        return "```\n" + "\n".join(lines) + "\n```"

    async def spin_and_update_gif(self, interaction):
        await interaction.response.defer()
        frames_grids = []
        grid = [["❓"]*3 for _ in range(3)]

        for _ in range(10):
            for r in range(3):
                for c in range(3):
                    grid[r][c] = random.choice(SLOT_SYMBOLS)
            frames_grids.append([row[:] for row in grid])

        self.grid = frames_grids[-1]  # Save last frame

        gif_bytes = generate_slot_gif(frames_grids)
        file = discord.File(fp=gif_bytes, filename="slot_spin.gif")
        await self.message.edit(content=None, attachments=[file], view=self)

        # Optionally, send the result text after
        result_text = self.get_result_text()
        await interaction.followup.send(result_text, ephemeral=False)

    def get_result_text(self):
        mid_row = self.grid[1]
        if mid_row[0] == mid_row[1] == mid_row[2]:
            return f"🎉 JACKPOT! Three {mid_row[0]}s!"
        elif mid_row[0] == mid_row[1] or mid_row[1] == mid_row[2] or mid_row[0] == mid_row[2]:
            return f"💰 Nice! You got two matching symbols!"
        else:
            return f"😢 No match. Try again!"

    @discord.ui.button(label="🎰 Spin", style=discord.ButtonStyle.green)
    async def spin_button(self, button, interaction):
        await self.spin_and_update_gif(interaction)

class SlotMachineCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="slots", description="Play the emoji slot machine!")
    async def slots(self, ctx: discord.ApplicationContext):
        view = SlotMachineView()
        msg = await ctx.respond("Loading slot machine...", view=view)
        sent = await msg.original_response()
        view.message = sent
        await sent.edit(content=view.render_grid(), view=view)

def setup(bot):
    bot.add_cog(SlotMachineCog(bot))
