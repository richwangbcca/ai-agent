from collections import defaultdict, deque
import os
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv
from agent import EventPlannerAgent

PREFIX = "!"

# Setup logging
logger = logging.getLogger("discord")

# Setup conversation history
conversation_history = defaultdict(lambda: deque(maxlen=5))

# Load the environment variables
load_dotenv()

# Create the bot with all intents
# The message content and members intent must be enabled in the Discord Developer Portal for the bot to work.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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


@bot.event
async def on_message(message: discord.Message):
    """
    Called when a message is sent in any channel the bot can see.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_message
    """
    # Don't delete this line! It's necessary for the bot to process commands.
    await bot.process_commands(message)

    # Ignore messages from self or other bots to prevent infinite loops.
    if not (message.author.bot or message.content.startswith("!")):
        # Process the message with the agent you wrote
        # Open up the agent.py file to customize the agent
        logger.info(f"Processing message from {message.author}: {message.content}")

        response = await agent.run(message, conversation_history[message.author.id])
        conversation_history[message.author.id].append("User: " + str(message.content))
        conversation_history[message.author.id].append("Me: " + str(response))
        logger.info(f"Conversation history: {str(list(conversation_history[message.author.id]))}")


        # Send the response back to the channel
        await message.reply(response)
    
    return

# Start the bot, connecting it to the gateway
bot.run(token)
