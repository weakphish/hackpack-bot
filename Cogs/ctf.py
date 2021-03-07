from asyncio.tasks import FIRST_COMPLETED
from logging import exception
from discord import message
from discord.channel import TextChannel
from discord.guild import Guild
from discord.member import Member

from discord.message import Message
from discord.raw_models import RawReactionActionEvent
from discord.role import Role
from API_Iterables.ctftime_iterable import CtfTimeEvents
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import asyncio


class CtfCog(commands.Cog, name='CTF Commands'):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.join_leave_start_str = f'{self.bot.command_prefix}ctf create '

    async def handle_ctf_reaction(self, payload: RawReactionActionEvent):
        guild: Guild = self.bot.get_guild(payload.guild_id)
        channel: TextChannel = guild.get_channel(payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)
        content = str(message.content)
        if content.startswith(self.join_leave_start_str):
            ctf: str = content[len(self.join_leave_start_str):]
            role: Role = discord.utils.get(guild.roles, name=ctf)
            member: Member = guild.get_member(payload.user_id)
            if payload.event_type == 'REACTION_ADD':
                await member.add_roles(role)
            else:
                await member.remove_roles(role)

    @commands.Cog.listener('on_raw_reaction_add')
    async def ctf_join_reaction(self, payload: RawReactionActionEvent):
        if str(payload.emoji) == '👍' and payload.user_id != self.bot.user.id:
            await self.handle_ctf_reaction(payload)

    @commands.Cog.listener('on_raw_reaction_remove')
    async def ctf_leave_reaction(self, payload):
        if str(payload.emoji) == '👍' and payload.user_id != self.bot.user.id:
            await self.handle_ctf_reaction(payload)

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
        forward = '➡'
        backward = '⬅'
        stop = '⏹️'
        delete = '🚮'
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
                done, pending = await asyncio.wait([self.bot.wait_for('raw_reaction_add', timeout=60, check=paginate_check),
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
        category = discord.utils.get(
            ctx.guild.categories, name=ctf_category_name)
        await ctx.guild.create_text_channel(name=ctf_name, overwrites=overwrites, category=category)
        message: Message = ctx.message
        await message.add_reaction('👍')

    @ctf.command(name="join")
    async def ctf_join(self, ctx: Context, ctf_name):
        """
        Join a CTF with the given name.
        """
        ctf_role = discord.utils.get(ctx.guild.roles, name=ctf_name)
        message: Message = ctx.message
        if ctf_role == None or ctf_role in message.author.roles:
            return
        await message.author.add_roles(ctf_role)
        await message.add_reaction('✅')

    @ctf.command(name="leave")
    async def ctf_leave(self, ctx: Context, ctf_name):
        """
        Leave a CTF you are in with the given name
        """
        ctf_role = discord.utils.get(ctx.guild.roles, name=ctf_name)
        message: Message = ctx.message
        if ctf_role == None or ctf_role not in message.author.roles:
            return
        await message.author.remove_roles(ctf_role)
        await message.add_reaction('✅')
