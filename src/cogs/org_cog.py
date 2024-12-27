import discord
import logfire
from discord.ext import commands

from src.forms.org_forms import CreateOrgForm
from src.untils import check_channel


class OrgCog(commands.Cog):
    """Club related cogs."""

    @discord.command(name="club_create")
    async def create_club(self, ctx):
        """Create a new Club. PRES ENTER."""
        with logfire.span("CREATE CLUB"):
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

    @discord.command(name="team_create")
    async def create_team(self, ctx):
        """Create a new Team. PRES ENTER."""
        org_type:str = "team"
        with logfire.span(f"CREATE {org_type.capitalize()}"):
            try:
                if not await check_channel(
                        ctx, ["team-admin"], f"This command can only be used in the `#{org_type}-admin` channel."
                ):
                    return
                create_form = CreateOrgForm(ctx, org_type=org_type)
                await ctx.response.send_modal(create_form)
            except Exception as e:
                logfire.error(f"Failed to create {org_type.capitalize()}: {e}", exc_info=True)
                await ctx.response.send_message(f"❌ Failed to create {org_type.capitalize()}.", ephemeral=True)



def setup(bot):
    """Pycord calls to setup the cog."""
    bot.add_cog(OrgCog(bot))  # add the cog to the bot


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
