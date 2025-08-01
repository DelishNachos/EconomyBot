import discord
import asyncio
import time
from cogs.stable_views import stable_view_factory

class StaminaGameView(discord.ui.View):
    def __init__(self, user_id, horse, interaction, on_complete, target_hold_time=3.0):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.horse = horse
        self.interaction = interaction
        self.on_complete = on_complete
        self.target_hold_time = target_hold_time
        self.start_time = None
        self.holding = False

        self.add_item(HoldButton(self))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self):
        if not self.holding:
            await self.on_complete(0.0, self.interaction)

class HoldButton(discord.ui.Button):
    def __init__(self, parent_view: StaminaGameView):
        super().__init__(label="Hold", style=discord.ButtonStyle.success)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if not self.parent_view.holding:
            self.label = "Release"
            self.style = discord.ButtonStyle.danger
            self.parent_view.holding = True
            self.parent_view.start_time = time.monotonic()
            await interaction.response.edit_message(view=self.parent_view)
        else:
            hold_duration = time.monotonic() - self.parent_view.start_time
            await self.parent_view.on_complete(hold_duration, self.parent_view.interaction)
            self.parent_view.stop()