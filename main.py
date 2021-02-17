from discord.flags import Intents
from API_Iterables.ctftime_iterable import CtfTimeEvents
from Cogs.crypto import CryptoCog
from Cogs.ctf import CtfCog
import discord
from discord.ext import commands
import json

intents = Intents.default()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!')


def load_config(filename: str) -> str:
    """
    Load the configuration file containing the bot's secret token and return it as a string
    """
    with open(filename, "r") as config:
        data = json.load(config)
        token = data["token"]
        return token

def main():
    token = load_config("config.json")
    bot.add_cog(CtfCog(bot))
    bot.add_cog(CryptoCog(bot))
    bot.run(token)


if __name__ == '__main__':
    main()
