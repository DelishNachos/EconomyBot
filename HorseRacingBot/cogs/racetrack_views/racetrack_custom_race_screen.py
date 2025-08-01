import asyncio
import discord
from discord.ui import InputText

from cogs.racetrack_views import racetrack_view_factory
from utils import db
from utils.odds_calculator import calculate_odds_defaults
from utils.race_simulator import simulate_custom_race

CUSTOM_RACE_BET_TIME = 30

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_main_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class RacetrackCustomRaceView(discord.ui.View):
    def __init__(self, user_id, custom_race_info):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(StartRaceButton(custom_race_info))
        self.add_item(SelectTrackButton(custom_race_info))
        self.add_item(SelectHorse1Button(custom_race_info))
        self.add_item(SelectHorse2Button(custom_race_info))
        self.add_item(SelectHorse3Button(custom_race_info))
        self.add_item(TogglePublicButton(custom_race_info))
        self.add_item(BackButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class StartRaceButton(discord.ui.Button):
    def __init__(self, custom_race_info):
        super().__init__(label="Start Race", style=discord.ButtonStyle.success)
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        is_ephemeral = not self.custom_race_info['public']
        await interaction.response.defer(ephemeral=is_ephemeral)

        horses = [
            self.custom_race_info["horse1"],
            self.custom_race_info["horse2"],
            self.custom_race_info["horse3"],
        ]

        track = self.custom_race_info['track']
        odds = calculate_odds_defaults(horses, track)

        # Step 1: Show betting interface
        bet_view = CustomRaceBetView(horses, CUSTOM_RACE_BET_TIME)  # You create this view to handle bets
        # Prepare embed for betting
        bet_embed = discord.Embed(
            title="🏇 Horse Race Starting!",
            description= f"Bet on a horse by clicking a button!\nTime left: {CUSTOM_RACE_BET_TIME} seconds",
            color=discord.Color.gold()
        )
        bet_embed.add_field(name="---------------------------------", value="", inline=False)
        bet_embed.add_field(name="Track Length", value=track['length'], inline=True)
        bet_embed.add_field(name="Track Tags", value=db.get_track_tags_as_string(track), inline=True)
        bet_embed.add_field(name="---------------------------------", value="", inline=False)
        for i, horse in enumerate(horses, 1):
            stats = f"Speed: {horse['speed']}, Stamina: {horse['stamina']}, Agility: {horse['agility']}\nOdds: {odds[horse['id']]['decimal_odds']}x"
            bet_embed.add_field(name=f"Horse {i}: {horse['name']}", value=stats, inline=False)
        bet_message = await interaction.followup.send(
            content=f"💰 Place your bets! You have {CUSTOM_RACE_BET_TIME} seconds.",
            embed=bet_embed,
            view=bet_view,
            ephemeral=is_ephemeral
        )

        # Countdown & update embed description
        for seconds_left in range(CUSTOM_RACE_BET_TIME - 1, -1, -1):
            bet_embed.description = f"Bet on a horse by clicking a button!\nTime left: {seconds_left} seconds"
            try:
                await bet_message.edit(embed=bet_embed)
            except Exception as e:
                print(f"Failed to edit message: {e}")
            await asyncio.sleep(1)

        # Step 3: Simulate the race
        race_results = simulate_custom_race(self.custom_race_info)

        # Step 4: Send race gif
        await interaction.followup.send(
            content="🏁 The race has begun!",
            file=discord.File(fp=race_results["gif_bytes"], filename="race.gif"),
            ephemeral=is_ephemeral
        )

        gif_duration_sec = race_results["gif_duration_ms"] / 1000
        await asyncio.sleep(gif_duration_sec + 1)

        # Step 6: Send results and payout
        response = racetrack_view_factory.racetrack_custom_race_results_screen(interaction.user.id, is_ephemeral, race_results, bet_view.bets, odds)
        
        await interaction.followup.send(
            content=response['content'],
            embed=response['embed'],
            view=response['view'],
            ephemeral=is_ephemeral
        )


class SelectTrackButton(discord.ui.Button):
    def __init__(self, custom_race_info):
        super().__init__(label="Track", style=discord.ButtonStyle.primary)
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        response = racetrack_view_factory.racetrack_custom_track_select_screen(interaction.user.id, self.custom_race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class SelectHorse1Button(discord.ui.Button):
    def __init__(self, custom_race_info):
        super().__init__(label="Horse #1", style=discord.ButtonStyle.primary)
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        response = await racetrack_view_factory.racetrack_custom_user_select_screen(interaction.user.id, self.custom_race_info, "horse1")
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class SelectHorse2Button(discord.ui.Button):
    def __init__(self, custom_race_info):
        super().__init__(label="Horse #2", style=discord.ButtonStyle.primary)
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        response = await racetrack_view_factory.racetrack_custom_user_select_screen(interaction.user.id, self.custom_race_info, "horse2")
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class SelectHorse3Button(discord.ui.Button):
    def __init__(self, custom_race_info):
        super().__init__(label="Horse #3", style=discord.ButtonStyle.primary)
        self.custom_race_info = custom_race_info

    async def callback(self, interaction: discord.Interaction):
        response = await racetrack_view_factory.racetrack_custom_user_select_screen(interaction.user.id, self.custom_race_info, "horse3")
        await interaction.response.edit_message(
            content=response["content"],
            embed=response["embed"],
            view=response["view"],
            attachments=[]
        )

class TogglePublicButton(discord.ui.Button):
    def __init__(self, custom_race_info):
        self.custom_race_info = custom_race_info
        label = "Public: ON" if custom_race_info['public'] else "Public: OFF"
        style = discord.ButtonStyle.success if custom_race_info['public'] else discord.ButtonStyle.danger
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        current_value = self.custom_race_info["public"]
        self.custom_race_info["public"] = not current_value

        response = racetrack_view_factory.racetrack_custom_race_screen(interaction.user.id, self.custom_race_info)
        await interaction.response.edit_message(
            content=response["content"],
            embeds=response["embeds"],
            view=response["view"],
            files=response['files']
        )



class CustomRaceBetView(discord.ui.View):
    def __init__(self, horses, timeout=15):
        super().__init__(timeout=timeout)
        self.bets = {}  # {user_id: {"horse_id": str, "amount": int}}
        self.horses = horses
        self.betting_open = True

        for horse in horses:
            self.add_item(CustomHorseBetButton(horse))

    def close_betting(self):
        self.betting_open = False
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True


class CustomHorseBetButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label=f"{horse['name']} 🐎", style=discord.ButtonStyle.primary, custom_id=horse["id"])
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        view: CustomRaceBetView = self.view

        if not view.betting_open:
            await interaction.response.send_message("❌ Betting is closed!", ephemeral=True)
            return

        await interaction.response.send_modal(CustomHorseBetModal(self.horse, view, interaction))


class CustomHorseBetModal(discord.ui.Modal):
    def __init__(self, horse, view: CustomRaceBetView, interaction: discord.Interaction):
        from utils import db

        super().__init__(title=f"Bet on {horse['name']} (💰 ${db.get_balance(interaction.user.id)})")
        self.horse = horse
        self.view = view

        self.bet_amount = InputText(
            label="Bet Amount",
            placeholder=f"Your balance: ${db.get_balance(interaction.user.id)}",
            required=True,
        )
        self.add_item(self.bet_amount)

    async def callback(self, interaction: discord.Interaction):
        from utils.db import get_balance  # Avoid circular import
        user_id = str(interaction.user.id)
        amount = self.bet_amount.value

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ Invalid bet amount.", ephemeral=True)
            return

        balance = get_balance(user_id)
        if amount > balance:
            await interaction.response.send_message("❌ You don't have enough money.", ephemeral=True)
            return

        self.view.bets[user_id] = {
            "horse_id": self.horse["id"],
            "amount": amount
        }

        await interaction.response.send_message(
            f"✅ You bet **${amount}** on **{self.horse['name']}**!", ephemeral=True
        )