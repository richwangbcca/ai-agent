from discord.ext import commands

class General(commands.Cog, name='General'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Pings the bot.")
    async def ping(ctx, *, arg=None):
        if arg is None:
            await ctx.send("Pong!")
        else:
            await ctx.send(f"Pong! Your argument was {arg}")

async def setup(bot: commands.Bot):
   await bot.add_cog(General(bot))