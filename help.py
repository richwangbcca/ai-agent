import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Event Planner Bot",
            description="Hello! 👋 I'm Event Planner Bot, and I can help you plan your next event. " +
            "I can help with basic logistics, budgeting, and venue selection, and I can automatically generate a Google Calendar event for your convenience. " +
            "You can use these provided commands for a structured approach, or you can communicate with me using natural language.",
            color=discord.Color.blue()
        )
        for cog, commands in mapping.items():
            command_list = [f"`{command.name}` - {command.help}" for command in commands]
            if command_list:
                embed.add_field(
                    name=cog.qualified_name if cog else "No Category",
                    value="\n".join(command_list),
                    inline=False
                )

        embed.set_footer(text="Use !help <command> for more details.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Command: {command.name}",
            description=command.help or "No description provided.",
            color=discord.Color.green()
        )
        embed.add_field(name="Usage", value=f"`{self.context.prefix}{command.qualified_name} {command.signature}`", inline=False)
        await self.get_destination().send(embed=embed)