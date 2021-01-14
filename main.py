import discord
import requests


client = discord.Client()


class HackpackBot(discord.Client):
    """
    The main bot class
    """
    async def on_ready(self):
        print("Hello, {0}!".format(self.user))

    @client.event
    async def on_message(message: discord.Message):
        if message.author != client.user and message.content.startswith('$hello'):
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
    client = HackpackBot()
    client.get_ctf_upcoming(100, 1422019499, 1423029499)
    client.run('token goes here')


if __name__ == '__main__':
    main()
