import asyncio
import time
import discord

from cogs.stable_views import stable_view_factory
from utils import db


import time
import asyncio

class SpeedGameView(discord.ui.View):
    def __init__(self, user_id, horse, interaction, on_complete, duration=10):
        super().__init__(timeout=None)  # Disable built-in timeout
        self.user_id = user_id
        self.horse = horse
        self.interaction = interaction
        self.on_complete = on_complete
        self.tap_count = {"count": 0}
        self.duration = duration
        self.start_time = time.monotonic()
        self.add_item(TapButton(self.tap_count))
        self._task = asyncio.create_task(self._timer())

    async def _timer(self):
        await asyncio.sleep(self.duration)
        self.stop()
        await self.on_complete(self.tap_count["count"], self.interaction)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self):
        # This won't be called because timeout=None
        pass
    
class TapButton(discord.ui.Button):
    def __init__(self, tap_count: dict):
        super().__init__(label="Tap!", style=discord.ButtonStyle.success)
        self.tap_count = tap_count

    async def callback(self, interaction: discord.Interaction):
        self.tap_count["count"] += 1
        await interaction.response.defer()

        