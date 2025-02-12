import discord
from discord.ext import commands


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        


def setup(bot):
    bot.add_cog(Tickets(bot=bot))