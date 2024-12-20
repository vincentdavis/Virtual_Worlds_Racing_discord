"""Main entry point for the bot."""
import os
from dotenv import load_dotenv
import logfire
from src.bot.client import VirtualWorldsBot
from src.utils.logger import setup_logging

# Configure logging first
setup_logging()

# Load environment variables
load_dotenv()

# Verify token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN or not TOKEN.strip():
    logfire.error("Discord bot token not found or empty!")
    raise ValueError("Invalid Discord bot token in .env file")

def main():
    """Start the bot."""
    try:
        logfire.info("Starting Virtual Worlds Racing Bot...")
        bot = VirtualWorldsBot()
        bot.run(TOKEN)
    except Exception as e:
        logfire.error(f"Failed to start bot: {str(e)}")
        raise
    finally:
        logfire.info("Bot shutdown complete")

if __name__ == "__main__":
    main()
