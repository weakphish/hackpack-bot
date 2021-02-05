import discord
from discord.ext import commands
from discord.ext.commands import Context
import requests
import json

client = discord.Client()
bot = commands.Bot(command_prefix='!')


def load_config(filename: str) -> str:
    """
    Load the configuration file containing the bot's secret token and return it as a string
    """
    with open(filename, "r") as config:
        data = json.load(config)
        token = data["token"]
        return token


@bot.command(name="hello")
async def ctf_hello(ctx: Context):
    await ctx.send("Hello!")


@bot.command(name="ctf-help")
async def ctf_help(ctx: Context):
    """
    Help function for the bot. Keep me updated!
    """
    desc = "Commands:\n!ctf-list: List upcoming CTFs\n!ctf-create <name>: Create a new CTF\n!ctf-join <name>: Join an ongoing CTF\n!ctf-leave <name>: Leave a CTF channel"
    embed_var = discord.Embed(title="Help", description=desc)
    await ctx.send(embed=embed_var)


@bot.command(name="ctf-list")
async def ctf_list(ctx: Context):
    """
    List upcoming CTFs. Usage: !ctf list
    """
    await ctx.send("Getting upcoming CTFs...")
    ctfs_upcoming = get_ctf_upcoming(15)
    for embed_var in ctfs_upcoming:
        await ctx.send(embed=embed_var)


@bot.command(name="ctf-create")
async def ctf_create(ctx: Context, ctf_name):
    """
    Create a CTF with a given name.
    """
    guild = bot.guilds[0]
    ctf_role = await guild.create_role(name=ctf_name)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.get_role(ctf_role.id): discord.PermissionOverwrite(read_messages=True)
    }
    ctf_category_name = "CTFs"
    category = discord.utils.get(guild.categories, name=ctf_category_name)
    await guild.create_text_channel(name=ctf_name, overwrites=overwrites, category=category)


@bot.command(name="ctf-join")
async def ctf_join(ctx: Context):
    guild = bot.guilds[0]
    ctf_name = ctx.message.content.split(" ")[2]
    ctf_role = discord.utils.get(guild.roles, name=ctf_name)
    await ctx.message.author.add_roles(ctf_role)
    # TODO fix this to be less annoying
    # await message.channel.send(f"Hey {message.author.name}, you've been added to {ctf_role.name}!")


@bot.command(name="ctf-leave")
async def ctf_leave(ctx: Context):
    guild = bot.guilds[0]
    ctf_name = ctx.message.content.split(" ")[2]
    ctf_role = discord.utils.get(guild.roles, name=ctf_name)
    await ctx.message.author.remove_roles(ctf_role)


def get_ctf_upcoming(limit: int):
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

        ctfs_upcoming.append(embed_var)

    return ctfs_upcoming


def main():
    token = load_config("config.json")

    bot.run(token)


if __name__ == '__main__':
    main()
