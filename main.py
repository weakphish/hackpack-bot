import discord
from discord.channel import CategoryChannel
import requests
import json

client = discord.Client()


def load_config(filename: str) -> str:
    """
    Load the configuration file containing the bot's secret token and return it as a string
    """
    with open(filename, "r") as config:
        data = json.load(config)
        token = data["token"]
        return token


class HackpackBot(discord.Client):
    """
    The main bot class
    """
    prefix = '!'

    async def on_ready(self):
        print("Hello, {0}!".format(self.user))

    @client.event
    async def on_message(self, message: discord.Message):
        """
        Handles message commands
        """
        if message.author == client.user:
            return
        # !hello - Says hello!
        if message.content.startswith(self.prefix + 'hello'):
            await message.channel.send("Hello!")
        # !ctf list - Lists upcoming CTFs from CTFtime
        if message.content.startswith(self.prefix + 'ctf') and "list" in message.content:
            await message.channel.send("Getting upcoming CTFs...")
            ctfs_upcoming = self.get_ctf_upcoming(5)
            for embed_var in ctfs_upcoming:
                await message.channel.send(embed=embed_var)
        # !ctf create ____ - Creates a new CTF event for the server with a role and channel
        elif message.content.startswith(self.prefix + 'ctf') and "create" in message.content:
            # This is a bit spaghetti, I am so sorry - John
            ctf_name = message.content.split(" ")[2]
            guild = self.guilds[0]
            ctf_role = await guild.create_role(name=ctf_name)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.get_role(ctf_role.id): discord.PermissionOverwrite(read_messages=True)
            }
            ctf_category_name = "CTFs"
            category = discord.utils.get(
                guild.categories, name=ctf_category_name)
            await guild.create_text_channel(name=ctf_name, overwrites=overwrites, category=category)
        # TODO !ctf join   ____ - Join the given CTF role / channel
        # TODO !ctf delete ____ - Remove CTF role and channel

    @client.event
    async def on_member_join(self, member):
        """
        Welcome new members to the server (welcome channel)
        """
        channel = client.get_channel(797912808082767923)
        await channel.send("Welcome, " + member.name + "!")

    def get_ctf_upcoming(self, limit: int):
        """
        Gets upcoming events from CTFTime. Takes a limit as a parameter and returns a discord embed
        that will be handled by the caller.
        """
        payload = {"limit": limit}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        url = "https://ctftime.org/api/v1/events/"

        response_json = requests.get(
            url, headers=headers, params=payload).json()

        #  Parse response for information
        ctfs_upcoming = []

        for i in range(limit):
            organizer_name = response_json[i]["organizers"][0]["name"]
            ctf_url = response_json[i]["ctftime_url"]
            ctf_format = response_json[i]["format"]
            logo_url = response_json[i]["logo"]
            ctf_title = response_json[i]["title"]
            ctf_desc = response_json[i]["description"]
            ctf_start = response_json[i]["start"]

            embed_var = discord.Embed(title=ctf_title, description=ctf_desc)
            embed_var.add_field(name="URL", value=ctf_url, inline=True)
            embed_var.add_field(
                name="Organizer", value=organizer_name, inline=True)
            embed_var.add_field(name="Format", value=ctf_format, inline=True)
            embed_var.add_field(name="Starts: ", value=ctf_start)
            embed_var.set_image(url=logo_url)

            ctfs_upcoming.append(embed_var)

        return ctfs_upcoming


def main():
    token = load_config("config.json")

    client = HackpackBot()
    client.run(token)


if __name__ == '__main__':
    main()
