from discord.ext import commands

class Event_Management(commands.Cog, name='Event Management'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="event", help="Create a new event, or switch the current event to the specified one.")
    async def event(ctx, *, arg=None):
        await ctx.send("TODO")

    @commands.command(name="list-events", help="List your current and actively planning events")
    async def list_events(ctx, *, arg=None):
        await ctx.send("TODO")

async def setup(bot: commands.Bot):
    await bot.add_cog(Event_Management(bot))