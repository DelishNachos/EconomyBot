import math
import random
import asyncio
import discord
from discord.ext import commands
from discord.ui import InputText
import os
import json
from utils import db
from utils.race_horse_manager import select_random_race_horses
from utils.track_generator import get_current_track_point
from utils.image_generator import generate_race_gif
from utils.odds_calculator import calculate_odds_by_simulation

betting_time = 30

num_of_track_points = 50
winner_delay = 1
max_stat = 150
max_stat_norm = max_stat / 10

energy_loss = 10

class HorseRaceView(discord.ui.View):
    def __init__(self, horses, timeout=30):
        super().__init__(timeout=timeout)
        self.bets = {}  # {user_id: {"horse_id": str, "amount": int}}
        self.horses = horses
        self.betting_open = True
        for horse in horses:
            self.add_item(HorseBetButton(horse))

    def close_betting(self):
        self.betting_open = False
        # Disable all buttons to indicate betting is closed
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

class HorseBetButton(discord.ui.Button):
    def __init__(self, horse):
        super().__init__(label=f"{horse['name']} 🐎", style=discord.ButtonStyle.primary, custom_id=horse["id"])
        self.horse = horse

    async def callback(self, interaction: discord.Interaction):
        view: HorseRaceView = self.view

        if not view.betting_open:
            await interaction.response.send_message("❌ Betting time is over. No more bets allowed.", ephemeral=True)
            return

        # Ask how much they want to bet
        await interaction.response.send_modal(HorseBetModal(self.horse, view, interaction))

class HorseBetModal(discord.ui.Modal):
    def __init__(self, horse, view: HorseRaceView, interaction: discord.Interaction):
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
        from utils.db import get_balance  # Avoid circular imports
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
            await interaction.response.send_message("❌ You don't have enough money for that bet.", ephemeral=True)
            return

        # Save the bet
        self.view.bets[user_id] = {
            "horse_id": self.horse["id"],
            "amount": amount
        }

        await interaction.response.send_message(
            f"✅ You bet **${amount}** on **{self.horse['name']}**!", ephemeral=True
        )

class HorseRacing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.race_in_progress = False
        self.current_race = None

    @discord.slash_command(name="randomrace", description="Start a new horse race with random horses", guild_ids=[int(os.getenv("DISCORD_GUILD_ID"))])
    async def startrace(
        self,
        ctx
    ):
        is_ephemeral = False
        
        if self.race_in_progress:
            await ctx.respond("🚫 A race is already in progress!", ephemeral=True)
            return

        await ctx.defer()
        
        horses = select_random_race_horses()
        track = db.get_random_race_track()
        track_length = track["track_steps"]

        track_data = db.get_track_data(track)
        corner_indices = track_data[-1].get("corner_indices", []) if isinstance(track_data[-1], dict) else []

        odds = calculate_odds_by_simulation(horses, track, track_data, corner_indices)

        # Simulate entire race upfront
        positions = {h["id"]: 0 for h in horses}
        positions_frames = []

        # Add randomness to house managed horses
        for horse in horses:
            if horse['owner'] == "house":
                horse['energy'] = random.randint(50, 100)

        energy_multipliers = {}
        for horse in horses:
            energy = horse['energy'] / 100  # Normalize to 0–1
            # Avoid math domain error by clamping very small energy values
            energy = max(energy, 0.001)
            multiplier = 1 + math.log(energy + 0.01) * 0.1
            multiplier = max(0, multiplier)  # Clamp to non-negative if needed
            energy_multipliers[horse["id"]] = multiplier


        while max(positions.values()) < track_length:
            for horse in horses:
                horse_id = horse["id"]
                progress = positions[horse_id]
                percentage_progress = progress / track_length

                path_index = get_current_track_point([tuple(p) for p in track_data[0]], percentage_progress)
                on_corner = path_index in corner_indices
                

                # Base weights
                speed_weight = 1.5
                stamina_weight = 1.2
                agility_weight = 1.0

                if on_corner:
                    agility_weight = 3.0


                # Normalize stats (0–100 input → 0–10 scale)
                norm_speed = horse["speed"] / max_stat_norm
                norm_stamina = horse["stamina"] / max_stat_norm
                norm_agility = horse["agility"] / max_stat_norm
                
                # Fatigue factor: increases as the horse approaches the end of the race
                fatigue_percent = progress / 60  # e.g. 0.8 = 80% through the race
                fatigue_penalty = fatigue_percent * (1 - norm_stamina / max_stat_norm)  # Higher stamina means lower penalty

                # Apply fatigue and energy penalty to effective speed
                effective_speed = norm_speed * (1 - 0.3 * fatigue_penalty)
                

                chance = (
                    (effective_speed * speed_weight) +
                    (norm_stamina * stamina_weight) +
                    (norm_agility * agility_weight)
                ) / 30

                # Apply energy penalty
                chance *= energy_multipliers[horse["id"]]

                if random.random() < chance:
                    positions[horse_id] += 1

            positions_frames.append(positions.copy())

        winning_horse_id = max(positions, key=positions.get)

        # Generate race GIF
        gif_bytes = generate_race_gif(horses, positions_frames, track, track_length, duration=200)

        # Prepare embed for betting
        embed = discord.Embed(
            title="🏇 Horse Race Starting!",
            description= f"Bet on a horse by clicking a button!\nTime left: {betting_time} seconds",
            color=discord.Color.gold()
        )
        embed.add_field(name="---------------------------------", value="", inline=False)
        embed.add_field(name="Track Length", value=track['length'], inline=True)
        embed.add_field(name="Track Tags", value=db.get_track_tags_as_string(track), inline=True)
        embed.add_field(name="---------------------------------", value="", inline=False)
        for i, horse in enumerate(horses, 1):
            stats = f"Speed: {horse['speed']}, Stamina: {horse['stamina']}, Agility: {horse['agility']}\nEnergy: {horse['energy']}%\nOdds: {odds[horse['id']]['decimal_odds']}x"
            embed.add_field(name=f"Horse {i}: {horse['name']}", value=stats, inline=False)

        view = HorseRaceView(horses)
        self.current_race = {
            "horses": horses,
            "view": view,
            "bets": {},
            "winning_horse_id": winning_horse_id,
            "gif_bytes": gif_bytes,
            "track_length": track_length,
            "gif_duration_ms": 200 * len(positions_frames)
        }
        self.race_in_progress = True

        # Send betting message with buttons
        
        message = await ctx.followup.send(embed=embed, view=view, ephemeral=is_ephemeral)

        # Countdown & update embed description
        for seconds_left in range(betting_time - 1, -1, -1):
            embed.description = f"Bet on a horse by clicking a button!\nTime left: {seconds_left} seconds"
            try:
                await message.edit(embed=embed)
            except Exception as e:
                print(f"Failed to edit message: {e}")
            await asyncio.sleep(1)

        # Close betting and disable buttons visually
        view.close_betting()
        try:
            await message.edit(view=view)
        except Exception as e:
            print(f"Failed to edit message to disable buttons: {e}")

        # Betting closed, send race GIF
        gif_file = discord.File(fp=self.current_race["gif_bytes"], filename="race.gif")
        await ctx.followup.send("🏇 The race is on!", file=gif_file, ephemeral=is_ephemeral)

        # Wait for GIF duration before sending results
        await asyncio.sleep((self.current_race["gif_duration_ms"] / 1000) + winner_delay)

        # Calculate payouts and send results
        await self.process_results(ctx, odds, is_ephemeral)

    async def process_results(self, ctx, odds, is_ephemeral):
        from utils.db import get_balance, update_balance, update_horse

        bets = self.current_race["view"].bets
        horses = self.current_race["horses"]
        horse_map = {h["id"]: h for h in horses}
        winning_horse_id = self.current_race["winning_horse_id"]


        results = [f"🎉 **{horse_map[winning_horse_id]['name']}** wins the race!\n"]
        
        total_house_cut = 0

        if not bets:
            results.append("⏹️ No one placed a bet.")

        total_bet_amount = 0
        for user_id, bet in bets.items():
            horse_id = bet["horse_id"]
            amount = bet["amount"]
            update_balance(user_id, -amount)
            total_bet_amount += amount
            if horse_id == winning_horse_id:
                payout = round(amount * odds[horse_id]["decimal_odds"])
                update_balance(user_id, payout)
                results.append(f"<@{user_id}> won ${payout}! 🤑")
                total_house_cut += round(amount * odds[horse_id]["house_payout"])
            else:
                results.append(f"<@{user_id}> lost ${amount}. 💸")
                total_house_cut += amount

        await ctx.followup.send("\n".join(results), ephemeral=is_ephemeral)

        update_balance("house", total_house_cut)

        for horse in horses:
            horse['races'] += 1

            if horse['id'] == winning_horse_id:
                horse['wins'] += 1
                if horse['owner'] and not horse['owner'] == "house":
                    owner_id = horse['owner']
                    user_bet = bets.get(user_id, {"horse_id": None, "amount": 0})
                    total_bet_amount -= user_bet['amount']
                    amount = int(total_bet_amount * db.get_general_config()['user_horse_winning_multiplier'])
                    db.add_money_to_user_saved(owner_id, amount)

            # if not horse['id'] == 'house':
            #     new_energy = horse['energy'] - energy_loss
            #     horse['energy'] = max(0, new_energy)
            
            update_horse(horse)

        self.race_in_progress = False
        self.current_race = None

def setup(bot):
    bot.add_cog(HorseRacing(bot))