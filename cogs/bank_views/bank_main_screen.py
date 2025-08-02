import discord
from cogs.bank_views import bank_view_factory
from utils import db

class BankMainView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

        self.add_item(SendMoneyButton())
        self.add_item(ClaimIncomeButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id


class SendMoneyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Send Money", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = SendMoneyDropdownView(sender=interaction.user)
        await interaction.response.edit_message(
            content="👤 Select a user to send money to:",
            view=view
        )

class ClaimIncomeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Claim Income", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        income_claimed = db.claim_income(interaction.user.id)

        response = bank_view_factory.bank_main_screen(interaction.user.id)
        await interaction.response.edit_message(
            content=f"Claimed ${income_claimed}",
            embed=response["embed"],
            view=response["view"]
        )

class SendMoneyDropdownView(discord.ui.View):
    def __init__(self, sender: discord.User):
        super().__init__(timeout=60)
        self.sender = sender

    @discord.ui.user_select(
        placeholder="Select a user to send money to",
        min_values=1,
        max_values=1
    )
    async def select_callback(self, select, interaction: discord.Interaction):
        recipient = select.values[0]
        if recipient.id == self.sender.id:
            await interaction.response.send_message("❌ You can't send money to yourself.", ephemeral=True)
            return

        # Show modal for amount input
        await interaction.response.send_modal(SendAmountModal(sender=self.sender, recipient=recipient))


class SendAmountModal(discord.ui.Modal):
    def __init__(self, sender: discord.User, recipient: discord.User):
        super().__init__(title="Send Money")
        self.sender = sender
        self.recipient = recipient

        self.amount_input = discord.ui.InputText(
            label="Amount to Send",
            placeholder="Enter amount (e.g., 100)",
            required=True,
        )
        self.add_item(self.amount_input)

    async def callback(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)

            if amount <= 0:
                response = bank_view_factory.bank_main_screen(interaction.user.id)
                await interaction.response.edit_message(
                    content="Amount must be greater than 0",
                    embed=response['embed'],
                    view=response['view']
                )
                return

            sender_balance = db.get_balance(self.sender.id)
            if sender_balance < amount:
                response = bank_view_factory.bank_main_screen(interaction.user.id)
                await interaction.response.edit_message(
                    content="You do not have enough money",
                    embed=response['embed'],
                    view=response['view']
                )
                return

            db.update_balance(self.sender.id, -amount)
            db.update_balance(self.recipient.id, amount)

            send_info = {
                "amount": amount,
                "recipient": self.recipient.id
            }

            response = await bank_view_factory.bank_sent_money_screen(interaction.user.id, send_info)
            await interaction.response.edit_message(
                content=response['content'],
                embed=response['embed'],
                view=response["view"]
            )

        except ValueError:
            response = bank_view_factory.bank_main_screen(interaction.user.id)
            await interaction.response.edit_message(
                content="Invalid Number Entered",
                embed=response['embed'],
                view=response['view']
            )