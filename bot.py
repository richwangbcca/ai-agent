from collections import defaultdict, deque
import os
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv

from agent import EventPlannerAgent
from help import CustomHelpCommand

PREFIX = "!"

# Setup logging
logger = logging.getLogger("discord")

# Setup conversation history
conversation_history = defaultdict(lambda: deque(maxlen=5))

# Load the environment variables
load_dotenv()

# Create the bot with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=CustomHelpCommand())

# Import the Mistral agent from the agent.py file
agent = EventPlannerAgent()

# Get the token from the environment variables
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    """
    Called when the client is done preparing the data received from Discord.
    Prints message on terminal when bot successfully connects to discord.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
    """
    logger.info(f"{bot.user} has connected to Discord!")
    await load_cogs() #TODO: change this to setup_hook


@bot.event
async def on_message(message: discord.Message):
    """
    Called when a message is sent in any channel the bot can see.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_message
    """
    await bot.process_commands(message)

    # Ignore messages from self or other bots to prevent infinite loops.
    if not (message.author.bot or message.content.startswith("!")):
        logger.info(f"Processing message from {message.author}: {message.content}")
        response = await agent.run(message, list(conversation_history[message.author.id]))
        conversation_history[message.author.id].append("User: " + str(message.content))
        conversation_history[message.author.id].append("Me: " + str(response))

        # Send the response back to the channel
        message_chunks = split_message(response)
        for chunk in message_chunks:
            await message.reply(chunk)
    
    return


def split_message(message, max_length=2000):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

async def load_cogs():
    await bot.load_extension("cogs.general")
    await bot.load_extension("cogs.event_mgmt")

# Start the bot, connecting it to the gateway
bot.run(token)
