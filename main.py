from typing import Any, Dict
from discord import channel
from discord.flags import Intents
from discord.guild import Guild
from discord.member import Member
from discord.message import Message
from discord.raw_models import RawReactionActionEvent
from discord.role import Role
from API_Iterables.ctftime_iterable import CtfTimeEvents
from Cogs.crypto import CryptoCog
from Cogs.ctf import CtfCog
import discord
from discord.ext import commands
import json


def load_config(filename: str) -> Dict[str, Any]:
    """
    Load the configuration file containing the bot's secret token and return it as a string
    """
    with open(filename, "r") as config:
        data = json.load(config)
        return {"token": data["token"], "prefix": data["prefix"]}


def main():
    config = load_config("config.json")
    intents: Intents = Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix=config["prefix"], intents=intents)
    bot.add_cog(CtfCog(bot))
    bot.add_cog(CryptoCog(bot))
    bot.activity = discord.Game(f"{config['prefix']}help")
    bot.run(config["token"])


if __name__ == '__main__':
    main()
