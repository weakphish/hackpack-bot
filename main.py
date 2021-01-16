import discord
import requests
import json

client = discord.Client()

def load_config(filename: str) -> str:
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
        if message.author != client.user and message.content.startswith(self.prefix + 'hello'):
            await message.channel.send("Hello!")
    
    def get_ctf_upcoming(self, number: int, start_timestamp: int, end_timestamp: int):
        """
        Gets upcoming events from CTFTime
        """
        payload = {"limit": number, "start": start_timestamp, "finish": end_timestamp}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url = "https://ctftime.org/api/v1/events/"
        r = requests.get(url, headers=headers, params=payload)


def main():
    token = load_config("config.json")

    client = HackpackBot()
    client.get_ctf_upcoming(100, 1422019499, 1423029499)
    client.run(token)


if __name__ == '__main__':
    main()
