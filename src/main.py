import discord


class HackpackBot(discord.Client):
    async def on_ready(self):
        print("Hello, {0}!".format(self.user))
    
    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(self.message))


def main():
    client = HackpackBot()
    client.run('token goes here')


if __name__ == '__main__':
    main()
