import discord
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
        if message.content.startswith(self.prefix + 'hello'):
            await message.channel.send("Hello!")
        if message.content.startswith(self.prefix + 'ctflist'):
            await message.channel.send("Getting upcoming CTFs...")
            self.get_ctf_upcoming(10)

    @client.event
    async def on_member_join(self, member):
        """
        Welcome new members to the server (welcome channel)
        """
        channel = client.get_channel(797912808082767923)
        await channel.send("Welcome, " + member.name + "!")

    def get_ctf_upcoming(self, limit: int):
        """
        Gets upcoming events from CTFTime
        """
        payload = {"limit": limit}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        url = "https://ctftime.org/api/v1/events/"

        response = requests.get(url, headers=headers, params=payload)
        print(response.json())


def main():
    token = load_config("config.json")

    client = HackpackBot()
    client.get_ctf_upcoming(100)
    client.run(token)


if __name__ == '__main__':
    main()
