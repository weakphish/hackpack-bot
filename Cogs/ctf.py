import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import requests


class CtfCog(commands.Cog, name='CTF Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def ctf(self, ctx: Context):
        """
        The CTF command group. To see all options do !help ctf
        """
        await ctx.send_help(ctx.command)
    
    @ctf.command()
    async def list(self, ctx: Context):
        """
        List upcoming CTFs. Usage: !ctf list
        """
        await ctx.send("Getting upcoming CTFs...")
        ctfs_upcoming = self.get_ctf_upcoming(15)
        for embed_var in ctfs_upcoming:
            await ctx.send(embed=embed_var)

    @ctf.command(name="create")
    async def ctf_create(self, ctx: Context, ctf_name):
        """
        Create a CTF with a given name.
        """
        ctf_role = await ctx.guild.create_role(name=ctf_name)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(ctf_role.id): discord.PermissionOverwrite(read_messages=True)
        }
        ctf_category_name = "CTFs"
        category = discord.utils.get(ctx.guild.categories, name=ctf_category_name)
        await ctx.guild.create_text_channel(name=ctf_name, overwrites=overwrites, category=category)

    @ctf.command(name="join")
    async def ctf_join(self, ctx: Context, ctf_name):
        ctf_role = discord.utils.get(ctx.guild.roles, name=ctf_name)
        await ctx.message.author.add_roles(ctf_role)
        # TODO fix this to be less annoying
        # await message.channel.send(f"Hey {message.author.name}, you've been added to {ctf_role.name}!")

    @ctf.command(name="leave")
    async def ctf_leave(ctx: Context, ctf_name):
        ctf_role = discord.utils.get(ctx.guild.roles, name=ctf_name)
        await ctx.message.author.remove_roles(ctf_role)

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

            embed_var = discord.Embed(title=ctf_title, description=ctf_desc, url=ctf_url)

            embed_var \
                .set_author(name=organizer_name, icon_url=logo_url) \
                .add_field(name="URL", value=ctf_url, inline=True) \
                .add_field(
                    name="Organizer", value=organizer_name, inline=True) \
                .add_field(name="Format", value=ctf_format, inline=True) \
                .add_field(name="Starts: ", value=ctf_start)

            ctfs_upcoming.append(embed_var)

        return ctfs_upcoming