import os
import discord
from cogs.shop_views.shop_main_screen import MainShopView
from cogs.shop_views.shop_horses_screen import ShopHorsesView
from cogs.shop_views.shop_item_screen import ShopItemView
from cogs.shop_views.shop_item_type_screen import ShopItemTypeView
from utils import db

def get_main_shop_view(user_id):
    return MainShopView(user_id)

def get_shop_horses_view(user_id, horses):
    return ShopHorsesView(user_id, horses)

def get_shop_item_view(user_id, item_types):
    return ShopItemView(user_id, item_types)

def get_shop_item_type_view(user_id, item_type):
    return ShopItemTypeView(user_id, item_type)

def main_shop_screen(user_id):
    content = None
    embed = discord.Embed(
        title=f"Welcome to the shop",
        description="Buy horses and items here",
        color=discord.Color.green()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    view = get_main_shop_view(user_id)

    return {
        "content": content,
        "embed": embed,
        "view": view
    }

def shop_horses_screen(user_id):
    embeds = []
    horses = db.load_daily_horses()

    content = None
    embed = discord.Embed(
        title=f"Welcome to the Horse Shop",
        description="Buy new horses here. Horses refresh every 24 hours",
        color=discord.Color.green()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embeds.append(embed)

    view = get_shop_horses_view(user_id, horses)

    

    for i, horse in enumerate(horses):
        embed = discord.Embed(title=f"Horse #{i+1}: {horse['name']}", color=discord.Color.blue())
        embed.add_field(name="Speed", value=horse["speed"])
        embed.add_field(name="Stamina", value=horse["stamina"])
        embed.add_field(name="Agility", value=horse["agility"])
        embed.add_field(name="Cost", value=f"${horse['market_price']}")
        embeds.append(embed)

    return {
        "content": content,
        "embeds": embeds,
        "view": view
    }

def shop_items_screen(user_id):
    content = None
    embed = discord.Embed(
        title=f"Welcome to the Item Shop",
        description="Here you can buy items to use on your horses",
        color=discord.Color.green()
    )
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    item_types = db.get_item_types()
    sorted_item_types =  sorted(item_types)

    return {
        "content": content,
        "embed": embed,
        "view": get_shop_item_view(user_id, sorted_item_types)
    }

def shop_item_type_screen(user_id, item_type):
    embeds = []

    content = None
    embed = discord.Embed(
        title=f"Welcome to the {item_type} shop",
        description="Please choose an item you would like to buy",
        color=discord.Color.green()
    )
    
    embed.set_author(name=f"💸 Balance: ${db.get_balance(user_id)}")
    embeds.append(embed)

    items = db.get_items_by_type(item_type)

    for item in items:
        embed = discord.Embed(title=f"{item['name']} (owned: X{db.get_user_item_count(user_id, item)})", description=item['description'], color=discord.Color.blue())
        embed.add_field(name="Energy Recovery", value=f"{item['energy']}%")
        embed.add_field(name="", value = "")
        embed.add_field(name="Cost", value=f"${item['cost']}")
        embeds.append(embed)

    return {
        "content": content,
        "embeds": embeds,
        "view": get_shop_item_type_view(user_id, item_type)
    }
