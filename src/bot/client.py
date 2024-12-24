"""Primary Client class that runs the bot"""

import discord as pycord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = pycord.Intents.default()
# intents.members = True
# intents.message_content = True


class VWRBot(commands.Bot):
    """VWRBot Client class that runs the bot"""

    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or("s!"), intents=intents)
