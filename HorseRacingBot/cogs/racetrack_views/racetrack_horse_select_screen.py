import discord

from cogs.racetrack_views import racetrack_view_factory
from utils import db


class BackButton(discord.ui.Button):
    def __init__(self, race_info):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.race_info = race_info

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_pre_race_screen(interaction.user.id, self.race_info)
        if not self.race_info['horse']:
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                attachments=response["attachments"]
            )
        else:
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
                file=response["file"]
            )

class RaceTrackHorseSelectView(discord.ui.View):
    def __init__(self, user_id, horses, race_info):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(HorseDropdown(user_id, horses, race_info))
        self.add_item(BackButton(race_info))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class HorseDropdown(discord.ui.Select):
    def __init__(self, user_id, horses, race_info):
        options = [
            discord.SelectOption(label=f"{horse['name']}: {horse['speed']}, {horse['stamina']}, {horse['agility']}, {horse['energy']}%", value=horse['id'])
            for horse in horses
        ]
        super().__init__(placeholder="Choose a horse...", options=options)
        self.user_id = user_id
        self.race_info = race_info

    async def callback(self, interaction: discord.Interaction):
        horse_id = self.values[0]
        self.race_info['horse'] = db.get_horse_by_id(horse_id)
        response = racetrack_view_factory.racetrack_pre_race_screen(self.user_id, self.race_info)

        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            file=response['file']
        )