import discord
import asyncio
import random


class AgilityGameView(discord.ui.View):
    def __init__(self, user_id, horse, interaction, on_complete):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.horse = horse
        self.interaction = interaction
        self.on_complete = on_complete
        self.signal_given = False
        self.start_time = None
        self.add_item(ReactButton(self))

        asyncio.create_task(self._signal_timer())

    async def _signal_timer(self):
        await asyncio.sleep(random.uniform(2, 5))
        self.signal_given = True
        for item in self.children:
            if isinstance(item, ReactButton):
                item.label = "NOW!"
                item.style = discord.ButtonStyle.success
                
        self.start_time = asyncio.get_event_loop().time()
        await self.interaction.edit_original_response(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id


class ReactButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="Wait...", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if not self.parent_view.signal_given:
            await self.parent_view.on_complete(False, 0.0, interaction)
        else:
            reaction_time = asyncio.get_event_loop().time() - self.parent_view.start_time
            await self.parent_view.on_complete(True, reaction_time, self.parent_view.interaction)
        self.parent_view.stop()