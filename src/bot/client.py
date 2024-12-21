"""Primary Client class that runs the bot"""

import discord as pycord
from discord.ext import commands

class VWRBot(commands.Bot):
    """VWRBot Client class that runs the bot"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_command(self.ping)
        self.add_command(self.register)
        self.add_command(self.whoami)
        self.add_command(self.whois)
        self.add_command(self.rider)
        self.add_command(self.riders
