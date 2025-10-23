import math
import random
import asyncio
import discord
from discord.ext import commands
from discord.ui import InputText
import os
import json
from utils import db
from utils import race_horse_manager
from utils.race_horse_manager import select_random_race_horses
from utils.track_generator import get_current_track_point
from utils.image_generator import generate_race_gif
from utils.odds_calculator import calculate_odds_by_simulation

betting_time = 30

num_of_track_points = 50
winner_delay = 1
max_stat = 150
max_stat_norm = max_stat / 10
race_energy_loss_per_tick = 10  # base energy loss per tick

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

    @discord.slash_command(name="randomrace", description="Start a new horse race with random horses", guild_ids=[int(id) for id in os.getenv("DISCORD_GUILD_ID").split(",")])
    async def startrace(
        self,
        ctx
    ):
        is_ephemeral = False
        steps = 0

        if self.race_in_progress:
            await ctx.respond("🚫 A race is already in progress!", ephemeral=True)
            return

        await ctx.defer()
        
        horses = race_horse_manager.select_close_random_race_horses()
        track = db.get_random_race_track()
        track_length = track["track_steps"]

        track_data = db.get_track_data(track)
        corner_indices = track_data[-1].get("corner_indices", []) if isinstance(track_data[-1], dict) else []

        odds = calculate_odds_by_simulation(horses, track, track_data, corner_indices)
        print("Calculated Odds")

        # Simulate entire race upfront
        positions = {h["id"]: 0 for h in horses}
        race_energy = {h["id"]: 100 for h in horses}  # start full energy
        positions_frames = []

        # Add randomness to house managed horses
        for horse in horses:
            if horse['owner'] == "house":
                horse['energy'] = random.randint(50, 100)

         # Precompute energy multipliers
        energy_multipliers = {}
        for h in horses:
            energy = h['energy'] / 100  # Normalize to 0–1
            energy = max(energy, 0.001)  # clamp low values
            #multiplier = 1 + math.log(energy + 0.01) * 0.1
            multiplier = .2 + math.sqrt(.64 * energy)
            energy_multipliers[h["id"]] = max(0, multiplier)


        while max(positions.values()) < track_length or steps > 1000:
            steps += 1
            for h in horses:
                horse_id = h["id"]
                progress = positions[horse_id]
                percentage_progress = progress / track_length

                path_index = get_current_track_point([tuple(p) for p in track_data[0]], percentage_progress)
                on_corner = path_index in corner_indices

                # Base stat weights, different on corners
                speed_weight = 2.0
                stamina_weight = 1.2
                agility_weight = .8
                if on_corner:
                    agility_weight = 1.8
                    speed_weight = 1.5
                    stamina_weight = 1.2

                # Normalize stats (0-150 to ~0-15)
                norm_speed = h["speed"] / max_stat_norm
                norm_stamina = h["stamina"] / max_stat_norm
                norm_agility = h["agility"] / max_stat_norm

                # Fatigue penalty (more fatigue with less stamina)
                fatigue_percent = progress / 60
                fatigue_penalty = fatigue_percent * (1 - norm_stamina / max_stat_norm)

                # Effective speed after fatigue
                effective_speed = norm_speed * (1 - 0.3 * fatigue_penalty)

                # Calculate base chance to move this tick
                chance = (
                    (effective_speed * speed_weight) +
                    (norm_stamina * stamina_weight) +
                    (norm_agility * agility_weight)
                ) / 30

                # Apply permanent energy multiplier
                chance *= energy_multipliers[horse_id]

                # Apply randomness to chance for natural variation
                chance *= random.uniform(0.9, 1.1)
                chance = min(chance, 0.95)  # cap max chance

                # Reduce race energy every tick based on stamina (higher stamina = less loss)
                energy_loss = race_energy_loss_per_tick * (1 - (h["stamina"] / max_stat))
                race_energy[horse_id] = max(0, race_energy[horse_id] - energy_loss)

                # === BURST MECHANIC ===
                burst_steps = 1  # default move 1 step

                # Randomize burst chance based on stamina with some variation
                base_burst_chance = 0.05 + (h["stamina"] / max_stat) * 0.2
                burst_chance = random.uniform(base_burst_chance * 0.7, base_burst_chance * 1.3)
                burst_chance = min(burst_chance, 0.3)

                if race_energy[horse_id] > 10 and random.random() < burst_chance:
                    max_burst = 1 + int((h["agility"] / max_stat) * 2)  # max 3 steps burst
                    # Weighted random burst steps: mostly small bursts, less big
                    burst_steps = random.choices(
                        population=[1, 2, 3],
                        weights=[0.7, 0.2, 0.1],
                        k=1
                    )[0]
                    burst_steps = min(burst_steps, max_burst)

                    # Variable energy cost per burst step
                    energy_cost = (burst_steps - 1) * random.randint(4, 6)

                    # Reduce burst steps if not enough energy
                    while burst_steps > 1 and race_energy[horse_id] < energy_cost:
                        burst_steps -= 1
                        energy_cost = (burst_steps - 1) * random.randint(4, 6)

                    # Deduct energy if burst
                    if burst_steps > 1:
                        race_energy[horse_id] -= energy_cost

                # Final movement roll
                if random.random() < chance:
                    positions[horse_id] += burst_steps

            positions_frames.append(positions.copy())


        # Find winner
        winning_horse_id = max(positions, key=positions.get)

        # Generate race GIF
        gif_bytes = generate_race_gif(horses, positions_frames, track, track_length, duration=200)
        print("Created Gif")

        embeds = []
        files = []
        # Prepare embed for betting
        bet_embed = discord.Embed(
            title="🏇 Horse Race Starting!",
            description= f"Bet on a horse by clicking a button!\nTime left: {betting_time} seconds",
            color=discord.Color.gold()
        )
        bet_embed.add_field(name="---------------------------------", value="", inline=False)
        bet_embed.add_field(name=f"Track: {track['name']}", value="", inline=False)
        bet_embed.add_field(name="Track Length", value=track['length'], inline=True)
        bet_embed.add_field(name="Track Tags", value=db.get_track_tags_as_string(track), inline=True)
        bet_embed.add_field(name="---------------------------------", value="", inline=False)
        embeds.append(bet_embed)
        for i, horse in enumerate(horses, 1):
            # Extract filename from the stored image_url path
            filename = os.path.basename(horse["image_url"]) if horse.get("image_url") else None
            
            if filename and os.path.exists(horse["image_url"]):
                file = discord.File(horse["image_url"], filename=filename)
            else:
                file = discord.File(db.default_horse_image_path(), filename=filename)

            horse_embed = discord.Embed(
                title=f"Horse {i}: {horse['name']}",
                color=discord.Color.gold()
            )
            horse_embed.add_field(name="Speed", value=horse['speed'], inline=True)
            horse_embed.add_field(name="Stamina", value=horse['stamina'], inline=True)
            horse_embed.add_field(name="Agility", value=horse['agility'], inline=True)
            horse_embed.add_field(name="Energy", value=f"{horse['energy']}%")
            horse_embed.add_field(name="Odds", value=f"{odds[horse['id']]['decimal_odds']}x")
            horse_embed.set_thumbnail(url=f"attachment://{filename}")
            embeds.append(horse_embed)
            files.append(file)

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
        
        message = await ctx.followup.send(embeds=embeds, view=view, files=files, ephemeral=is_ephemeral)

        # Countdown & update embed description
        for seconds_left in range(betting_time - 1, -1, -1):
            embeds[0].description = f"Bet on a horse by clicking a button!\nTime left: {seconds_left} seconds"
            try:
                await message.edit(embeds=embeds)
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
                results.append(f"<@{user_id}> won ${payout} (+${payout - amount})! 🤑")
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
                    user_bet = bets.get(owner_id, {"horse_id": None, "amount": 0})
                    total_bet_amount -= user_bet['amount']

                    decimal_odds = odds[horse['id']]['decimal_odds']
                    scaling_factor = math.exp(0.8 * decimal_odds - 1) + 0.18
                    bet_multiplier = min(.75, db.get_general_config()['user_horse_winning_multiplier'] * scaling_factor)
                    amount = int(total_bet_amount * bet_multiplier)
                    db.add_money_to_user_saved(owner_id, amount)

            # if not horse['id'] == 'house':
            #     new_energy = horse['energy'] - energy_loss
            #     horse['energy'] = max(0, new_energy)
            
            update_horse(horse)

        self.race_in_progress = False
        self.current_race = None

def setup(bot):
    bot.add_cog(HorseRacing(bot))