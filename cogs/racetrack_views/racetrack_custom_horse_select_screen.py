import discord

from cogs.racetrack_views import racetrack_view_factory
from utils import db


class BackButton(discord.ui.Button):
    def __init__(self, custom_race_info, custom_horse_id):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.custom_race_info = custom_race_info
        self.custom_horse_id = custom_horse_id

    async def callback(self, interaction: discord.Interaction):
        response = await racetrack_view_factory.racetrack_custom_user_select_screen(interaction.user.id, self.custom_race_info, self.custom_horse_id)
        await interaction.response.edit_message(
                content=response["content"],
                embed=response["embed"],
                view=response["view"]
            )

class RacetrackCustomHorseSelectView(discord.ui.View):
    def __init__(self, user_id, horses, custom_race_info, custom_horse_id):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(HorseDropdown(user_id, horses, custom_race_info, custom_horse_id))
        self.add_item(BackButton(custom_race_info, custom_horse_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

class HorseDropdown(discord.ui.Select):
    def __init__(self, user_id, horses, custom_race_info, custom_horse_id):
        selected_horse_ids = {
            horse["id"]
            for key, horse in custom_race_info.items()
            if key != custom_horse_id and horse is not None
        }

        options = []
        for horse in horses:
            is_selected_elsewhere = horse["id"] in selected_horse_ids
            label = f"{horse['name']}: {horse['speed']}, {horse['stamina']}, {horse['agility']}"
            if is_selected_elsewhere:
                label = f"~~{horse['name']}: {horse['speed']}, {horse['stamina']}, {horse['agility']}~~"  # visually show it's already taken

            options.append(
                discord.SelectOption(
                    label=label,
                    value=horse["id"],
                    description="Already selected by another slot" if is_selected_elsewhere else None
                )
            )

        super().__init__(placeholder="Choose a horse...", options=options)
        self.user_id = user_id
        self.custom_race_info = custom_race_info
        self.custom_horse_id = custom_horse_id
        self.selected_horse_ids = selected_horse_ids

    async def callback(self, interaction: discord.Interaction):
        horse_id = self.values[0]

        # If the horse was already selected for another slot, deselect this slot
        if horse_id in self.selected_horse_ids:
            self.custom_race_info[self.custom_horse_id] = None
        else:
            self.custom_race_info[self.custom_horse_id] = db.get_horse_by_id(horse_id)

        response = racetrack_view_factory.racetrack_custom_race_screen(
            self.user_id, self.custom_race_info
        )

        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"],
            files=response["files"]
        )