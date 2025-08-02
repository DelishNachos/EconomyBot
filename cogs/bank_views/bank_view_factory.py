import discord
from cogs.bank_views.bank_main_screen import BankMainView
from cogs.bank_views.bank_sent_money_screen import BankSentMoneyView
from utils import db


def get_bank_main_view(user_id):
    return BankMainView(user_id)

def get_bank_send_money_view(user_id):
    return BankSentMoneyView(user_id)

def bank_main_screen(user_id):
    balance = db.get_balance(user_id)


    content = None
    embed = discord.Embed(
        title=f"Welcome to the Bank",
        description="See your account, send money to other users, and claim your passive income here",
        color=discord.Color.green()
    )
    embed.set_author(name=f"💸 Balance: ${balance}")
    embed.add_field(name="Balance", value=f"${balance}", inline=False)
    embed.add_field(name="Income", value=f"${db.calculate_per_hour_income(user_id)}/hr")
    embed.add_field(name="Income to Claim", value=f"${int(db.get_updated_saved_income(user_id))}")
    embed.set_footer(text=f"Max passive income store of 24 hours")
    view = get_bank_main_view(user_id)

    return {
        "content": content,
        "embed": embed,
        "view": view
    }

async def bank_sent_money_screen(user_id, send_info):
    recipient_name = await db.get_user_name(send_info['recipient'])
    content = None
    embed = discord.Embed(
        title=f"Sent the Money",
        description=f"Sent ${send_info['amount']} to {recipient_name}",
        color=discord.Color.green()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    view = get_bank_send_money_view(user_id)

    return {
        "content": content,
        "embed": embed,
        "view": view
    }