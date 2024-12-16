import os

import discord as pycord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

bot = pycord.Bot()


@bot.slash_command()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")


@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")


#
# Get the token from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    print(pycord.__version__)
    if not TOKEN:
        raise ValueError("No token found! Make sure to set DISCORD_BOT_TOKEN in your .env file.")
    bot.run(TOKEN)
