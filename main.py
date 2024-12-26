"""Main bot file."""

import logfire

logfire.configure()

from dotenv import load_dotenv  # noqa: E402

from src.bot.client import init_bot  # noqa: E402

# Load environment variables from .env file
load_dotenv()


init_bot()
