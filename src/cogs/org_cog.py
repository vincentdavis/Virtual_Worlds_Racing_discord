import discord
import logfire
from discord.ext import commands

from src.extras.roles_mgnt import BaseRole, check_user_roles
from src.extras.untils import check_channel
from src.forms.org_forms import CreateOrgForm


class OrgCog(commands.Cog):
    """Club related cogs."""

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    clubs = discord.SlashCommandGroup("club", "Club management commands.")
    teams = discord.SlashCommandGroup("team", "Team management commands.")

    @clubs.command(name="create")
    async def create_club(self, ctx):
        """Create a new Club. PRES ENTER."""
        with logfire.span("CREATE CLUB"):
            check_reg, msg, roles = await check_user_roles(
                ctx, discord_id=ctx.author.id, role_filter=BaseRole.REGISTERED
            )
            if not check_reg:
                await ctx.response.send_message(
                    f"Error: {msg}",
                    ephemeral=True,
                )
                return
            check_mem, msg, roles = await check_user_roles(
                ctx, discord_id=ctx.author.id, role_filter=BaseRole.CLUB_MEMBER
            )
            if check_mem:
                await ctx.response.send_message(
                    "Error: You are already a member of a club. You cannot create a new club.",
                    ephemeral=True,
                )
                return
            try:
                if not await check_channel(
                    ctx, ["club-admin"], "This command can only be used in the `#club-admin` channel."
                ):
                    return
                create_form = CreateOrgForm(ctx, org_type="club")
                await ctx.response.send_modal(create_form)
            except Exception as e:
                logfire.error(f"Failed to create club: {e}", exc_info=True)
                await ctx.response.send_message("❌ Failed to create club.", ephemeral=True)

    @teams.command(name="create")
    async def create_team(self, ctx):
        """Create a new Team. PRES ENTER."""
        org_type: str = "team"
        with logfire.span("CREATE TEAM"):
            try:
                check_reg, msg, roles = await check_user_roles(
                    ctx, discord_id=ctx.author.id, role_filter=BaseRole.REGISTERED
                )
                if not check_reg:
                    await ctx.response.send_message(
                        f"Error: {msg}",
                        ephemeral=True,
                    )
                    return
                check_mem, msg, roles = await check_user_roles(
                    ctx, discord_id=ctx.author.id, role_filter=BaseRole.CLUB_ADMIN
                )
                if check_mem:
                    await ctx.response.send_message(
                        "Error: You must be a CLUB_ADMIN to create a team",
                        ephemeral=True,
                    )
                    return
                create_form = CreateOrgForm(ctx, org_type=org_type)
                await ctx.response.send_modal(create_form)
            except Exception as e:
                logfire.error(f"Failed to create {org_type.capitalize()}: {e}", exc_info=True)
                await ctx.response.send_message(f"❌ Failed to create {org_type.capitalize()}.", ephemeral=True)

    @clubs.command(name="review_join_requets")
    async def review_join_requests(self, ctx):
        """Review join requests for the club."""
        with logfire.span("REVIEW JOIN REQUESTS"):
            try:
                check_reg, msg, roles = await check_user_roles(
                    ctx, discord_id=ctx.author.id, role_filter=BaseRole.REGISTERED
                )
                if not check_reg:
                    await ctx.response.send_message(
                        f"Error: {msg}",
                        ephemeral=True,
                    )
                    return
                check_mem, msg, roles = await check_user_roles(
                    ctx, discord_id=ctx.author.id, role_filter=BaseRole.CLUB_ADMIN
                )
                if not check_mem:
                    await ctx.response.send_message(
                        "Error: You must be a CLUB_ADMIN to review join requests.",
                        ephemeral=True,
                    )
                    return
                await ctx.response.send_message("Review join requests.")
            except Exception as e:
                logfire.error(f"Failed to review join requests: {e}", exc_info=True)
                await ctx.response.send_message("❌ Failed to review join requests.", ephemeral=True)


def setup(bot):
    """Pycord calls to setup the cog."""
    try:
        bot.add_cog(OrgCog(bot))  # add the cog to the bot
        logfire.info("OrgCog loaded successfully.")
    except Exception as e:
        logfire.error(f"Failed to load OrgCog: {e}", exc_info=True)
        raise e


# # Add a team to a club
# @bot.command(name="add_team")
# async def add_team(ctx, club_name: str, team_name: str):
#     """Add a team to a club."""
#     rider = await Rider.find_one({"discord_id": ctx.author.id})
#     if not rider:
#         await ctx.send("You must be a registered rider to add a team.")
#         return
#
#     club = await Club.find_one({"name": club_name})
#     if not club:
#         await ctx.send(f"Club '{club_name}' not found.")
#         return
#
#     if rider not in club.admins:
#         await ctx.send("You must be an admin of this club to add a team.")
#         return
#
#     team = await Team.find_one({"name": team_name})
#     if not team:
#         await ctx.send(f"Team '{team_name}' not found.")
#         return
#
#     await club.add_team(team)
#     await ctx.send(f"Team '{team.name}' added to club '{club.name}'.")
#
#
# # Remove a team from a club
# @bot.command(name="remove_team")
# async def remove_team(ctx, club_name: str, team_name: str):
#     """Remove a team from a club."""
#     discord_id = ctx.author.id
#     rider = await Rider.find_one({"discord_id": ctx.author.id})
#     if not rider:
#         await ctx.send("You must be a registered rider to remove a team.")
#         return
#
#     club = await Club.find_one(Club.name == club_name)
#     if not club:
#         await ctx.send(f"Club '{club_name}' not found.")
#         return
#
#     if rider not in club.admins:
#         await ctx.send("You must be an admin of this club to remove a team.")
#         return
#
#     team = await Team.find_one(Team.name == team_name)
#     if not team:
#         await ctx.send(f"Team '{team_name}' not found.")
#         return
#
#     await club.remove_team(team)
#     await ctx.send(f"Team '{team.name}' removed from club '{club.name}'.")
#
#

# # Mark a club as inactive
# @bot.command(name="mark_inactive")
# async def mark_inactive(ctx, club_name: str):
#     """Mark a club as inactive."""
#     discord_id = ctx.author.id
#     rider = await Rider.find_one({"discord_id": ctx.author.id})
#     if not rider:
#         await ctx.send("You must be a registered rider to mark a club as inactive.")
#         return
#
#     club = await Club.find_one(Club.name == club_name)
#     if not club:
#         await ctx.send(f"Club '{club_name}' not found.")
#         return
#
#     if rider not in club.admins:
#         await ctx.send("You must be an admin of this club to mark it as inactive.")
#         return
#
#     await club.mark_inactive()
#     await ctx.send(f"Club '{club.name}' marked as inactive.")
#
#
# # Mark a club as active
# @bot.command(name="mark_active")
# async def mark_active(ctx, club_name: str):
#     """Mark a club as active."""
#     discord_id = ctx.author.id
#     rider = await Rider.find_one({"discord_id": ctx.author.id})
#     if not rider:
#         await ctx.send("You must be a registered rider to mark a club as active.")
#         return
#
#     club = await Club.find_one(Club.name == club_name)
#     if not club:
#         await ctx.send(f"Club '{club_name}' not found.")
#         return
#
#     if rider not in club.admins:
#         await ctx.send("You must be an admin of this club to mark it as active.")
#         return
#
#     await club.mark_active()
#     await ctx.send(f"Club '{club.name}' marked as active.")
