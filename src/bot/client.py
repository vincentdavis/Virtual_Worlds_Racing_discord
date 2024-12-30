"""Primary Client class that runs the bot"""

from os import getenv

import discord as pycord
import logfire
from dotenv import load_dotenv

from src.database.db_models import init_peewee_db

load_dotenv()


def init_bot():
    """Initialize the bot."""
    with logfire.span("STARTING BOT"):
        logfire.info("Load pycord intents")
        intents = pycord.Intents.default()
        # intents.messages = True
        # intents.message_content = True  # Required for message commands
        # intents.members = True  # Required for member-based interactions like lookup
        logfire.info("Initialize bot")
        bot = pycord.Bot(command_prefix="!", intents=pycord.Intents.all())
        logfire.info("Run bot")

        @bot.event
        async def on_ready():
            """Initialize PeeWee connection."""
            logfire.info("Initialize PeeWee connection.")

            init_peewee_db()

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
        async def test_hello(ctx, name: str | None = None):
            """Test command to say hello."""
            logfire.info("test_hello command")
            name = name or ctx.author.name
            await ctx.respond(f"Hello {name}!")
            logfire.info(f"Hello {name}! Done")

        bot.load_extension("src.cogs.rider_cog")
        # bot.load_extension("src.cogs.membership_cog")
        bot.load_extension("src.cogs.org_cog")

        logfire.info("Get: DISCORD_BOT_TOKEN")
        TOKEN = getenv("DISCORD_BOT_TOKEN")
        if not TOKEN:
            logfire.error("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
            raise ValueError("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
        bot.run(TOKEN)
        logfire.info("Bot started: if your here it has stopped")
