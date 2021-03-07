import base64
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

supported_bases = "The only current supported bases are 16, 32, and 64"


class CryptoCog(commands.Cog, name='Crypto Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def encode(self, ctx: Context):
        """
        All defined encoding methods currently available through this bot
        """
        await ctx.send_help(ctx.command)

    @encode.command(name='base')
    async def base_encode(self, ctx: Context, _base: int, *message):
        """
        Encode a UTF-8 message using base X where X is the base you pass in .
        """
        message = ' '.join(message).encode('utf-8')
        if (_base == 16):
            message = base64.b16encode(message)
        elif (_base == 32):
            message = base64.b32encode(message)
        elif (_base == 64):
            message = base64.b64encode(message)
        else:
            await ctx.send(supported_bases)
            return

        await ctx.send(f'```\n{message}\n```')

    @encode.command(name='urlsafe64')
    async def urlsafe64encode(self, ctx: Context, *message):
        """
        Encode using the URL - and filesystem-safe alphabet(which substitutes \- instead of \+ and \_ instead of \/) a message using base 64.
        """
        message = ' '.join(message).encode('utf-8')
        await ctx.send(f'```\n{base64.urlsafe_b64encode(message)}\n```')

    @commands.group(invoke_without_command=True)
    async def decode(self, ctx):
        """
        All defined decoding methods currently available through this bot
        """
        await ctx.send_help(ctx.command)

    @decode.command(name='base')
    async def base_decode(self, ctx: Context, _base: int, *message):
        """
        Decode a message using base X where X is the base you pass in .
        """
        message = ' '.join(message).encode('utf-8')
        if (_base == 16):
            message = base64.b16decode(message)
        elif (_base == 32):
            message = base64.b32decode(message)
        elif (_base == 64):
            message = base64.b64decode(message)
        else:
            await ctx.send(supported_bases)
            return

        await ctx.send(f'```\n{message}\n```')

    @decode.command(name='urlsafe64')
    async def urlsafe64decode(self, ctx, *message):
        """
        Decode using the URL - and filesystem-safe alphabet(which substitutes \- instead of \+ and \_ instead of \/) a message using base 64.
        """
        message = ' '.join(message).encode('utf-8')
        await ctx.send(f'```\n{base64.urlsafe_b64decode(message)}\n```')
