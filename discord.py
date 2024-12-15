import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot with prefix and intents
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot successfully connects to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_member_join(member):
    """Event triggered when a new member joins the server."""
    # Send welcome message to the system channel if it exists
    if member.guild.system_channel:
        await member.guild.system_channel.send(
            f'Welcome {member.mention} to {member.guild.name}!'
        )

@bot.command(name='ping')
async def ping(ctx):
    """Simple command to check if the bot is responsive."""
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.command(name='info')
async def server_info(ctx):
    """Command to display basic server information."""
    guild = ctx.guild
    embed = discord.Embed(
        title=f'{guild.name} Server Information',
        description='Basic server statistics',
        color=discord.Color.blue()
    )

    # Add fields to embed
    embed.add_field(name='Server Owner', value=guild.owner.display_name, inline=False)
    embed.add_field(name='Member Count', value=guild.member_count, inline=True)
    embed.add_field(name='Channel Count', value=len(guild.channels), inline=True)
    embed.add_field(name='Role Count', value=len(guild.roles), inline=True)

    # Set server icon as thumbnail if it exists
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await ctx.send(embed=embed)

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int):
    """
    Command to clear specified number of messages from the channel.
    Only users with 'manage_messages' permission can use this command.
    """
    if amount < 1:
        await ctx.send('Please specify a positive number of messages to delete.')
        return

    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
    await ctx.send(f'Deleted {len(deleted)-1} messages.', delete_after=5)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for command errors."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument. Please check the command usage.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Get the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("No token found! Make sure to set DISCORD_TOKEN in your .env file.")
    bot.run(TOKEN)