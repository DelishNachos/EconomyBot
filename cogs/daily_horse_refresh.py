from discord.ext import tasks, commands

from utils import db

class DailyHorseRefresh(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.refresh_task.start()

    def cog_unload(self):
        self.refresh_task.cancel()

    @tasks.loop(hours=6)
    async def refresh_task(self):
        db.refresh_daily_horses()

    @refresh_task.before_loop
    async def before_refresh_task(self):
        await self.bot.wait_until_ready()  # ensures the bot is ready

def setup(bot):
    bot.add_cog(DailyHorseRefresh(bot))