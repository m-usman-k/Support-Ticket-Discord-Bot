import discord, os
from discord.ext import commands

from dotenv import load_dotenv

# Environment Variables:
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot:
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Events:
@bot.event
async def on_ready():

    await bot.load_extension("extensions.Tickets")

    await bot.tree.sync()

    print(f"🟢 | Bot running as {bot.user.name}")




bot.run(BOT_TOKEN)