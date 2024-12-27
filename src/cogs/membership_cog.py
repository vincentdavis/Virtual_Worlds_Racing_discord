import discord
import logfire
from discord.ext import commands

from src.database.db_models import User
from src.vwr_exceptions import NotAClubAdmin, UserNotRegistered


class MembershipCog(commands.Cog):
    """Club related cogs."""

    @discord.user_command(name="Club: Add as admin")
    async def add_club_admin(self, ctx, target_user: discord.Member):
        """Add the selected user to the list of admins for a selected club."""
        with logfire.span("Add Admin to Club"):
            logfire.info(f"Target user: {target_user}")
            try:
                target_user_obj = User.get_or_none(User.discord_id == target_user.id)
                requesting_user_obj = User.get_or_none(User.discord_id == ctx.author.id)
                if not target_user_obj:
                    logfire.error("Target User not found")
                    raise UserNotRegistered(f"{target_user} Is not registered")

                if not requesting_user_obj.club_admin:
                    logfire.error("Requesting User is not a club admin")
                    raise NotAClubAdmin(f"{ctx.author} is not a club admin")
                if target_user_obj.club_id != requesting_user_obj.club_id:
                    logfire.error(f"Target User is not in the club: {requesting_user_obj.club_id.name}")
                    raise NotAClubAdmin(f"{target_user} is not in a club")
            except Exception as e:
                logfire.error(f"Failed to add admin to club: {e}")
                return await ctx.respond("❌ An error occurred while adding admin.", ephemeral=True)

            async def callback(interaction):
                try:
                    target_user_obj.club_admin = True
                    target_user_obj.update()
                    ctx.response(
                        "✅ '{target_user.display_name}' has been added as an admin to club '{selected_club.name}'.",
                        ephemeral=True,
                    )
                except Exception as e:
                    logfire.error(f"Failed to add admin to club: {e}")
                    # raise e
                    await ctx.respond("❌ An error occurred while adding admin.", ephemeral=True)

    @discord.user_command(name="Team: Add as admin")
    async def add_team_admin(self, ctx, target_user: discord.Member):
        """Add the selected user to the list of admins for a selected club."""
        with logfire.span("Add Admin to Team"):
            logfire.info(f"Target user: {target_user}")
            try:
                target_user_obj = User.get_or_none(User.discord_id == target_user.id)
                requesting_user_obj = User.get_or_none(User.discord_id == ctx.author.id)
                if not target_user_obj:
                    logfire.error("Target User not found")
                    raise UserNotRegistered(f"{target_user} Is not registered")

                if not requesting_user_obj.club_admin:
                    logfire.error("Requesting User is not a team admin")
                    raise NotAClubAdmin(f"{ctx.author} is not a team admin")
                if target_user_obj.club_id != requesting_user_obj.club_id:
                    logfire.error(f"Target User is not in the team: {requesting_user_obj.club_id.name}")
                    raise NotAClubAdmin(f"{target_user} is not in a tea")
            except Exception as e:
                logfire.error(f"Failed to add admin to tea: {e}")
                return await ctx.respond("❌ An error occurred while adding admin.", ephemeral=True)

            async def callback(interaction):
                try:
                    target_user_obj.club_admin = True
                    target_user_obj.update()
                    ctx.response(
                        f"✅ '{target_user.display_name}' has been added as an admin to team'.",
                        ephemeral=True,
                    )
                except Exception as e:
                    logfire.error(f"Failed to add admin to team: {e}")
                    # raise e
                    await ctx.respond("❌ An error occurred while adding admin.", ephemeral=True)

def setup(bot):
    """Pycord calls to setup the cog."""
    bot.add_cog(MembershipCog(bot))  # add the cog to the bot


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
