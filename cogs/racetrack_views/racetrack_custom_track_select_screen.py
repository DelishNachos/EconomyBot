import discord

from cogs.racetrack_views import racetrack_view_factory
from utils import db


class BackButton(discord.ui.Button):
    def __init__(self, custom_race_info):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_custom_race_screen(interaction.user.id, self.custom_race_info)
        await interaction.response.edit_message(
                content=response["content"],
                embeds=response["embeds"],
                view=response["view"],
                files=response['files']
            )

class RacetrackCustomTrackSelectView(discord.ui.View):
    def __init__(self, user_id, tracks, custom_race_info):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(TrackDropdown(user_id, tracks, custom_race_info))
        self.add_item(BackButton(custom_race_info))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class TrackDropdown(discord.ui.Select):
    def __init__(self, user_id, tracks, custom_race_info):
        # Add a "Random Track" option first
        options = [discord.SelectOption(label="🎲 Random Track", value="_random_")]

        # Add all actual track options
        options += [
            discord.SelectOption(
                label=f"{track['name']}: {track['length']}, {db.get_track_tags_as_string(track)}",
                value=track['id']
            )
            for track in tracks
        ]
        super().__init__(placeholder="Choose a track...", options=options)
        self.user_id = user_id
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        track_id = self.values[0]
        if (track_id == "_random_"):
            self.custom_race_info['track'] = db.get_random_race_track()
        else:
            self.custom_race_info['track'] = db.get_track_by_id(track_id)
        response = racetrack_view_factory.racetrack_custom_race_screen(self.user_id, self.custom_race_info)

        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"],
            files=response['files']
        )