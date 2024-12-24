import discord
import logfire
from discord.ext import commands

from src.database.db_models import Membership, Rider


class MembershipCog(commands.Cog):
    """Club related cogs."""

    @discord.user_command(name="Club: add admin")
    async def add_admin(self, ctx, target_user: discord.Member):
        """Add the invoking user to the list of admins for a selected club."""
        logfire.info("Add Admin to Club")
        try:
            if not await Rider.is_registered(ctx):
                await ctx.respond("❌ You must be registered to manage club admins.", ephemeral=True)
                return

            rider = await Rider.find_one({"discord_id": ctx.author.id})
            logfire.info(f"Rider: {rider} with id: {rider.id}")
            if not rider:
                await ctx.respond("❌ Rider profile not found.", ephemeral=True)
                return

            admin_clubs = await Membership.get_user_membership(
                membership_type=[
                    "Club_admin",
                ],
                rider=rider,
            )
            logfire.info(f"Admin Clubs: {admin_clubs}")
            if not admin_clubs:
                await ctx.respond("❌ You are not listed as an admin for any clubs.", ephemeral=True)
                return

            options = [discord.SelectOption(label=club.name, value=str(club.id)) for club in admin_clubs]
            if not options:
                await ctx.respond("❌ No clubs are available for admin modification.", ephemeral=True)
                return

            select_menu = discord.ui.Select(
                placeholder="Select a club to add yourself as an admin...",
                options=options,
            )

            async def callback(interaction):
                selected_club_id = interaction.data["values"][0]
                selected_club = await Membership.find_one({"_id": selected_club_id})

                if not selected_club:
                    await interaction.response.send_message("❌ Club no longer exists.", ephemeral=True)
                    return

                if target_user.id in [admin.discord_id for admin in selected_club.admins]:
                    await interaction.response.send_message(
                        f"❌ '{target_user.display_name}' is already an admin for club '{selected_club.name}'.",
                        ephemeral=True,
                    )
                    return

                new_admin = await Rider.find_one({"discord_id": target_user.id})
                if not new_admin:
                    await interaction.response.send_message("❌ Target user is not a registered rider.", ephemeral=True)
                    return

                await selected_club.add_admin(new_admin)
                await interaction.response.send_message(
                    f"✅ '{target_user.display_name}' has been added as an admin to club '{selected_club.name}'.",
                    ephemeral=True,
                )

            select_menu.callback = callback
            view = discord.ui.View()
            view.add_item(select_menu)

            await ctx.send("Please select a club:", view=view)

        except Exception as e:
            logfire.error(f"Failed to add admin to club: {e}")
            raise e
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
