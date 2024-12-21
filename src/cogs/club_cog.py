import discord
import logfire
from discord.ext import commands

from src.forms.club_forms import ClubForm
from src.untils import check_channel, is_registered


class ClubCog(commands.Cog):
    """Club related cogs."""

    @discord.command(name="club_create")
    async def create_club(self, ctx):
        """Create a new club and assign the invoking user as an admin."""
        with logfire.span("CREATE CLUB"):
            try:
                if not await is_registered(ctx):
                    return
                if not await check_channel(
                    ctx, ["club-admin"], "This command can only be used in the `#club-admin` channel."
                ):
                    return
            except Exception as e:
                logfire.error(f"Failed to create club: Failed requirement checks: {e}")
                await ctx.respond("❌ Failed to create club.", ephemeral=True)
                return
            create_form = ClubForm()
            await ctx.response.send_modal(create_form)


def setup(bot):
    """Pycord calls to setup the cog."""
    bot.add_cog(ClubCog(bot))  # add the cog to the bot


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
# # Add an admin to a club
# @bot.command(name="add_admin")
# async def add_admin(ctx, club_name: str, admin_discord_id: int):
#     """Add an admin to a club."""
#     rider = await Rider.find_one({"discord_id": ctx.author.id})
#     if not rider:
#         await ctx.send("You must be a registered rider to add an admin.")
#         return
#
#     club = await Club.find_one({"name": club_name})
#     if not club:
#         await ctx.send(f"Club '{club_name}' not found.")
#         return
#
#     if rider not in club.admins:
#         await ctx.send("You must be an admin of this club to add another admin.")
#         return
#
#     new_admin = await Rider.find_one({"discord_id": ctx.author.id})
#     if not new_admin:
#         await ctx.send(f"No rider found with Discord ID {admin_discord_id}.")
#         return
#
#     await club.add_admin(new_admin)
#     await ctx.send(f"Rider '{new_admin.name}' added as an admin to club '{club.name}'.")
#
#
# # Remove an admin from a club
# @bot.command(name="remove_admin")
# async def remove_admin(ctx, club_name: str, admin_discord_id: int):
#     """Remove an admin from a club."""
#     discord_id = ctx.author.id
#     rider = await Rider.find_one({"discord_id": ctx.author.id})
#     if not rider:
#         await ctx.send("You must be a registered rider to remove an admin.")
#         return
#
#     club = await Club.find_one(Club.name == club_name)
#     if not club:
#         await ctx.send(f"Club '{club_name}' not found.")
#         return
#
#     if rider not in club.admins:
#         await ctx.send("You must be an admin of this club to remove another admin.")
#         return
#
#     existing_admin = await Rider.find_one({"discord_id": admin_discord_id})
#     if not existing_admin:
#         await ctx.send(f"No rider found with Discord ID {admin_discord_id}.")
#         return
#
#     try:
#         await club.remove_admin(existing_admin)
#         await ctx.send(f"Rider '{existing_admin.name}' removed as an admin from club '{club.name}'.")
#     except ValueError as e:
#         await ctx.send(f"Error: {e!s}")
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
