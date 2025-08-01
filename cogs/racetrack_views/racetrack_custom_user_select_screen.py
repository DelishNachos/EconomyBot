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

class RacetrackCustomUserSelectView(discord.ui.View):
    def __init__(self, user_id, user_dropdown, custom_race_info):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(user_dropdown)
        self.add_item(BackButton(custom_race_info))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class UserDropdown(discord.ui.Select):
    def __init__(self, options, user_id, custom_race_info, custom_horse_id):
        super().__init__(placeholder="Choose a User...", options=options)
        self.user_id = user_id
        self.custom_race_info = custom_race_info
        self.custom_horse_id = custom_horse_id

    @classmethod
    async def create(cls, user_id, users, custom_race_info, custom_horse_id):
        options = [discord.SelectOption(label="🎲 Random Horse", value="_random_")]

        user_labels = {}
        for uid in users:
            if uid == 'house':
                user_labels[uid] = 'House'
            else:
                user_labels[uid] = await db.get_user_name(int(uid))

        options += [
            discord.SelectOption(
                label=f"{user_labels[uid]}: Horse count: {len(db.get_user_public_horses(uid))}",
                value=uid
            )
            for uid in users
        ]

        return cls(options, user_id, custom_race_info, custom_horse_id)

    async def callback(self, interaction: discord.Interaction):
        chosen_user_id = self.values[0]
        if chosen_user_id == "_random_":
            already_selected_ids = {
                horse['id']
                for key in ('horse1', 'horse2', 'horse3')
                if (horse := self.custom_race_info.get(key)) is not None and isinstance(horse, dict) and key != self.custom_horse_id
            }
            random_horses = db.get_random_public_horses(1, exclude_ids=already_selected_ids)
            if random_horses:
                self.custom_race_info[self.custom_horse_id] = random_horses[0]
            else:
                self.custom_race_info[self.custom_horse_id] = None  # or handle no available horses

            response = racetrack_view_factory.racetrack_custom_race_screen(interaction.user.id, self.custom_race_info)
            await interaction.response.edit_message(
                content=response["content"],
                embeds=response["embeds"],
                view=response["view"],
                files=response["files"]
            )
        else:
            response = racetrack_view_factory.racetrack_custom_horse_select_screen(
                interaction.user.id, chosen_user_id, self.custom_race_info, self.custom_horse_id
            )
            await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"],
            )