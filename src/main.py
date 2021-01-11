import discord

class HackpackBot(discord.Client):
    async def on_ready(self):
        print("Hello, {0}!".format(self.user))

