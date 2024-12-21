"""Main bot file."""

# ruff: noqa: I001
# ruff: noqa: E402
import logfire
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logfire.configure()

# ruff: I001: on
# ruff: E402 on
import os

import discord as pycord
from beanie import init_beanie

from motor.motor_asyncio import AsyncIOMotorClient

from src.database.db_models import Rider, Team, Club

with logfire.span("STARTING BOT"):
    # Get the token from environment variables
    logfire.info("Get: DISCORD_BOT_TOKEN")
    intents = pycord.Intents.default()
    # intents.messages = True
    # intents.message_content = True  # Required for message commands
    # intents.members = True  # Required for member-based interactions like lookup
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        logfire.error("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
        raise ValueError("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
    logfire.info("Initialize bot")
    bot = pycord.Bot(command_prefix="!", intents=pycord.Intents.all())

    # bot = pycord.Bot(intents=pycord.Intents.all())
    logfire.info("Run bot")


@bot.event
async def on_ready():
    """Initialize MongoDB connection, Beanie ORM."""
    logfire.info("Initialize Beanie ORM")
    client = AsyncIOMotorClient(
        os.getenv("MONGO_URL"),
    )
    db_name = os.getenv("MONGO_DB")
    await init_beanie(
        database=client[db_name],  # Specify database here
        document_models=[Rider, Team, Club],  # Specify document models here
    )
    logfire.info("Beanie ORM initialized")
    # Sync commands
    try:
        logfire.info("Syncing commands with Discord...")
        await bot.sync_commands()
        logfire.info("Commands synced successfully!")
    except Exception as e:
        logfire.error(f"Failed to sync commands: {e}")
    logfire.info("Bot is now ready!")


@bot.user_command(name="Say Hello")
async def test_hi(ctx, user):
    """Say hello to a user."""
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")


@bot.slash_command(command_prefix="!")
async def test_hello(ctx, name: str = None):
    """Test command to say hello."""
    logfire.info("test_hello command")
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")
    logfire.info(f"Hello {name}! Done")


bot.load_extension("src.cogs.rider_cog")
bot.load_extension("src.cogs.club_cog")


# Get the token from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot.run(TOKEN)
logfire.info("Bot started: if your here it has stopped")

# if __name__ == "__main__":
#     print(pycord.__version__)
#     TOKEN = os.getenv("DISCORD_BOT_TOKEN")
#     if not TOKEN:
#         raise ValueError("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
#     bot.run(TOKEN)
