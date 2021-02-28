from asyncio.tasks import FIRST_COMPLETED
from logging import exception
from API_Iterables.ctftime_iterable import CtfTimeEvents
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import asyncio


class CtfCog(commands.Cog, name='CTF Commands'):
    def __init__(self, bot):
        self.bot: discord.Client = bot

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
        forward='➡'
        backward='⬅'
        stop='⏹️'
        delete ='🚮'
        emojis = [forward, backward, stop, delete]
        msg: discord.Message = await ctx.send("Getting upcoming CTFs...")
        ctfs_upcoming = CtfTimeEvents()
        await msg.add_reaction(backward)
        await msg.add_reaction(forward)
        await msg.add_reaction(stop)
        await msg.add_reaction(delete)
        await msg.edit(content=None, embed=ctfs_upcoming.current())
        def paginate_check(payload: discord.RawReactionActionEvent):
            emoji = str(payload.emoji)
            author: discord.User = ctx.author
            return payload.user_id == author.id and payload.message_id == msg.id and (emoji in emojis) 
        while True:
            try:
                done, pending = await asyncio.wait([self.bot.wait_for('raw_reaction_add', timeout=60, check=paginate_check), \
                                                    self.bot.wait_for('raw_reaction_remove', timeout=60, check=paginate_check)], return_when=FIRST_COMPLETED)

                for i in pending:
                    i.cancel()

                if len(done) == 0:
                    raise asyncio.TimeoutError

                payload = done.pop().result()
                emoji = str(payload.emoji)
                if emoji == forward:
                    await msg.edit(embed=ctfs_upcoming.next())
                elif emoji == backward:
                    await msg.edit(embed=ctfs_upcoming.prev())
                elif emoji == stop:
                    for e in emojis:
                        await msg.remove_reaction(e, self.bot.user)
                    return
                elif emoji == delete:
                    await msg.delete()
                    return
            except asyncio.TimeoutError:
                for e in emojis:
                    await msg.remove_reaction(e, self.bot.user)
                return
            except:
                return

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
