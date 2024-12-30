"""Utilities for managing categories and channels."""

import discord
import logfire


async def create_on_guild(ctx, org_type: str, club_name: str | None = None, team_name: str | None = None):
    """Create a new club Category or Team Channel on the server."""
    # Make sure we have categories Clubs and Teams
    try:
        if org_type == "club":
            logfire.info("Get the category named 'CLUBS' in the server")
            guild = ctx.guild
            category = discord.utils.get(guild.categories, name="CLUBS")

            logfire.info("Create Text channel under the 'CLUBS' category")
            club_channel = await guild.create_text_channel(name=club_name, category=category)
            club_channel = await guild.create_role(name=club_name, category=category)

            logfire.info("Club channel created")
            await ctx.respond(
                f"✅ Club '{club_name}' has been created successfully! Check it out here: {club_channel.mention}"
            )
        elif org_type == "team":
            logfire.info("Get the channel named 'TEAMS' in the server")
            guild = ctx.guild
            category = discord.utils.get(guild.categories, name="TEAMS")
            logfire.info("Create Text channel under the 'TEAMS' category")
            team_channel = await guild.create_text_channel(name=team_name, category=category)
            logfire.info("Club channel created")
            await ctx.respond(
                f"✅ Team '{team_name}' has been created successfully! Check it out here: {team_channel.mention}"
            )

    except Exception as e:
        logfire.error(f"Failed to create club: {e}")
        await ctx.respond("❌ Failed to create club. An error occurred.", ephemeral=True)
