"""Main bot file."""

# ruff: noqa: I001
# ruff: noqa: E402
import logfire

from rider_cmd import RegistrationForm, lookup_user

logfire.configure()

# ruff: I001: on
# ruff: E402 on
import os

import discord as pycord
from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from db_models import Rider, Club, Team

# Load environment variables from .env file
load_dotenv()


with logfire.span("Starting bot"):
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
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    await init_beanie(
        database=client.VIRTUAL_WORLDS_RACING,  # Specify database here
        document_models=[Rider, Team, Club],  # , Team, Club],
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


####################################################################################################
#### Rider Commands ##############################################################################
####################################################################################################


@bot.slash_command(name="register")
async def register(ctx):
    """Register a new rider. Press  enter: Only works in the '#rider-admin' channel."""
    # Check if the command is used in the 'rider-admin' channel
    if ctx.channel.name not in ["rider-admin", "bot-testing"]:
        await ctx.respond("This command can only be used in the `#rider-admin` channel.", ephemeral=True)
        logfire.warn(f"{ctx.author} tried to register outside of the rider-admin channel.")
        return

    # Allow the command to proceed if in the correct channel
    await ctx.response.send_modal(RegistrationForm())


@bot.slash_command(name="lookup")
async def lookup(ctx, user: pycord.Member):
    """Look up a user in the registration database."""
    try:
        await lookup_user(ctx, user)
    except Exception as e:
        logfire.error(f"Failed to lookup user: {e}")
        await ctx.respond("❌ Failed to lookup user", ephemeral=True)


@bot.command(name="create_club")
async def create_club(ctx, name: str, zp_club_id: int = None):
    """Create a new club and assign the invoking user as an admin."""
    try:
        logfire.info(f"Creating club '{name}'")
        rider = await Rider.find_one({"discord_id": ctx.author.id})
        if not rider:
            logfire.warn("User not found")
            await ctx.send("You must be a registered rider to create a club.")
            return
        if ctx.channel.name not in ["club-admin", "bot-testing"]:
            logfire.warn("Wrong channel")
            await ctx.respond("This command can only be used in the `#club-admin` channel.", ephemeral=True)
            return
    except Exception as e:
        logfire.error(f"Failed to create club: Failed requirement checks: {e}")
        await ctx.send("❌ Failed to create club.")
    try:
        club_exists = await Club.find_one({"name": name})
        if club_exists:
            logfire.warn("Club already exists")
            await ctx.send(f"❌ Club '{name}' already exists.")
            return
        logfire.info("Creating club object")
        rider = await Rider.find_one({"discord_id": ctx.author.id})
        club = await Club.create_club(name=name, creator=rider, zp_club_id=zp_club_id)
        await ctx.send(f"Club '{club.name}' successfully created!")
    except ValueError as e:
        await ctx.send(f"❌ Error: {e!s}")
        logfire.error(f"Failed to create club: {e}")
    except Exception as e:
        logfire.error(f"Failed to create club: {e}")
        await ctx.send("❌ Failed to create club. Unknown error.")


# Add a team to a club
@bot.command(name="add_team")
async def add_team(ctx, club_name: str, team_name: str):
    """Add a team to a club."""
    rider = await Rider.find_one({"discord_id": ctx.author.id})
    if not rider:
        await ctx.send("You must be a registered rider to add a team.")
        return

    club = await Club.find_one({"name": club_name})
    if not club:
        await ctx.send(f"Club '{club_name}' not found.")
        return

    if rider not in club.admins:
        await ctx.send("You must be an admin of this club to add a team.")
        return

    team = await Team.find_one({"name": team_name})
    if not team:
        await ctx.send(f"Team '{team_name}' not found.")
        return

    await club.add_team(team)
    await ctx.send(f"Team '{team.name}' added to club '{club.name}'.")


# Remove a team from a club
@bot.command(name="remove_team")
async def remove_team(ctx, club_name: str, team_name: str):
    """Remove a team from a club."""
    discord_id = ctx.author.id
    rider = await Rider.find_one({"discord_id": ctx.author.id})
    if not rider:
        await ctx.send("You must be a registered rider to remove a team.")
        return

    club = await Club.find_one(Club.name == club_name)
    if not club:
        await ctx.send(f"Club '{club_name}' not found.")
        return

    if rider not in club.admins:
        await ctx.send("You must be an admin of this club to remove a team.")
        return

    team = await Team.find_one(Team.name == team_name)
    if not team:
        await ctx.send(f"Team '{team_name}' not found.")
        return

    await club.remove_team(team)
    await ctx.send(f"Team '{team.name}' removed from club '{club.name}'.")


# Add an admin to a club
@bot.command(name="add_admin")
async def add_admin(ctx, club_name: str, admin_discord_id: int):
    """Add an admin to a club."""
    rider = await Rider.find_one({"discord_id": ctx.author.id})
    if not rider:
        await ctx.send("You must be a registered rider to add an admin.")
        return

    club = await Club.find_one({"name": club_name})
    if not club:
        await ctx.send(f"Club '{club_name}' not found.")
        return

    if rider not in club.admins:
        await ctx.send("You must be an admin of this club to add another admin.")
        return

    new_admin = await Rider.find_one({"discord_id": ctx.author.id})
    if not new_admin:
        await ctx.send(f"No rider found with Discord ID {admin_discord_id}.")
        return

    await club.add_admin(new_admin)
    await ctx.send(f"Rider '{new_admin.name}' added as an admin to club '{club.name}'.")


# Remove an admin from a club
@bot.command(name="remove_admin")
async def remove_admin(ctx, club_name: str, admin_discord_id: int):
    """Remove an admin from a club."""
    discord_id = ctx.author.id
    rider = await Rider.find_one({"discord_id": ctx.author.id})
    if not rider:
        await ctx.send("You must be a registered rider to remove an admin.")
        return

    club = await Club.find_one(Club.name == club_name)
    if not club:
        await ctx.send(f"Club '{club_name}' not found.")
        return

    if rider not in club.admins:
        await ctx.send("You must be an admin of this club to remove another admin.")
        return

    existing_admin = await Rider.find_one({"discord_id": admin_discord_id})
    if not existing_admin:
        await ctx.send(f"No rider found with Discord ID {admin_discord_id}.")
        return

    try:
        await club.remove_admin(existing_admin)
        await ctx.send(f"Rider '{existing_admin.name}' removed as an admin from club '{club.name}'.")
    except ValueError as e:
        await ctx.send(f"Error: {e!s}")


# Mark a club as inactive
@bot.command(name="mark_inactive")
async def mark_inactive(ctx, club_name: str):
    """Mark a club as inactive."""
    discord_id = ctx.author.id
    rider = await Rider.find_one({"discord_id": ctx.author.id})
    if not rider:
        await ctx.send("You must be a registered rider to mark a club as inactive.")
        return

    club = await Club.find_one(Club.name == club_name)
    if not club:
        await ctx.send(f"Club '{club_name}' not found.")
        return

    if rider not in club.admins:
        await ctx.send("You must be an admin of this club to mark it as inactive.")
        return

    await club.mark_inactive()
    await ctx.send(f"Club '{club.name}' marked as inactive.")


# Mark a club as active
@bot.command(name="mark_active")
async def mark_active(ctx, club_name: str):
    """Mark a club as active."""
    discord_id = ctx.author.id
    rider = await Rider.find_one({"discord_id": ctx.author.id})
    if not rider:
        await ctx.send("You must be a registered rider to mark a club as active.")
        return

    club = await Club.find_one(Club.name == club_name)
    if not club:
        await ctx.send(f"Club '{club_name}' not found.")
        return

    if rider not in club.admins:
        await ctx.send("You must be an admin of this club to mark it as active.")
        return

    await club.mark_active()
    await ctx.send(f"Club '{club.name}' marked as active.")


#
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
