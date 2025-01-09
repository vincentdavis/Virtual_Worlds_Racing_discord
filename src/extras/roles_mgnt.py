"""Module to manage roles in the discord server."""

from collections import abc
from collections.abc import Iterable
from enum import Enum
from typing import Literal

import discord
import discord.ext.commands
import logfire
from discord import Role


class BaseRole(Enum):
    """Filter terms to search roles."""

    ADMIN = "ADMIN"
    REGISTERED = "REGISTERED"
    CLUB_MEMBER = "CLUB_MEMBER"
    TEAM_MEMBER = "TEAM_MEMBER"
    CLUB_ADMIN = "CLUB_ADMIN"
    TEAM_ADMIN = "TEAM_ADMIN"


async def list_roles(ctx: discord.ext.commands.Context, role_filter: BaseRole | Iterable[BaseRole]) -> list:
    """List roles matching the provided filter term.

    Args:
        ctx (discord.ext.commands.Context): The context object.
        role_filter (BaseRole | Iterable[BaseRole]): The role name to search for.

    Returns:
        list: A list of role objects that match the filter term.

    """
    try:
        # Get all roles from the guild
        roles = await ctx.guild.fetch_roles()

        if isinstance(filter, BaseRole):
            filtered_roles = [role for role in roles if role.name == role_filter.value]
            return filtered_roles
        elif isinstance(filter, abc.Iterable):
            filtered_roles = [role for role in roles if role.name in [r.value for r in role_filter]]
            return filtered_roles
        else:
            return []

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return []


async def check_user_roles(
    ctx: discord.ext.commands.Context,
    discord_id: int,
    role_filter: BaseRole | Iterable[BaseRole],
) -> tuple[bool, str, list[Role]] | tuple[bool, str, None]:
    """Check if the user has Any or All the roles in the filter term.

    Args:
        ctx (discord.ext.commands.Context): The context object.
        discord_id (int): The discord ID of the user to search for roles.
        role_filter (BaseRole): The role name to search for.

    """
    logfire.info(f"Checking server roles for {discord_id}, with {role_filter}")
    try:
        member = ctx.guild.get_member(discord_id)
        logfire.info(f"discord_id: {member} has roles: {member.roles}")
        filtered_roles = [role for role in member.roles if role.name == role_filter.value]
        logfire.info(f"Filtered roles: {filtered_roles}")
        if filtered_roles:
            return True, f"{member} has a matching role.", filtered_roles
        else:
            return False, f"{member} does not have required server role.", filtered_roles

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return False, f"Failed to check server roles. {role_filter}", None


async def add_base_role(
    ctx: discord.ext.commands.Context, discord_id: int, role_filter: BaseRole
) -> discord.Member | None:
    """Add a role to a user based on the provided filter term.

    Args:
        ctx (discord.ext.commands.Context): The context object.
        discord_id (int): The discord ID of the user to search for roles.
        role_filter (BaseRole | Iterable[BaseRole]): The role name to search for.

    """
    try:
        member = ctx.guild.get_member(discord_id)  # Get the member corresponding to discord_id
        # Filter roles based on the provided filter_term
        role = discord.utils.get(ctx.guild.roles, name=role_filter.value)
        await member.add_roles(role)
        return ctx.guild.get_member(discord_id)

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return None


async def club_member_roles(
    ctx: discord.ext.commands.Context,
    discord_id: int,
    action: Literal["add", "remove"],
    club_channel: str | int | None,
) -> discord.Member | None:
    """Add or remove the discord_id from the club channel role.

    Each club channel has a role with the same name as the channel.

    Args:
    ctx (discord.ext.commands.Context): The context object.
    discord_id (int): The discord ID of the user to search for roles.
    action (Literal["add", "remove"]): The action to perform.
    channel_channel (str | int | None): The channel object or name or id of the channel.

    """
    try:
        member = ctx.guild.get_member(discord_id)  # Get the member corresponding to discord_id

        if isinstance(club_channel, str):
            channel = discord.utils.get(ctx.guild.channels, name=club_channel)
        elif isinstance(club_channel, int):
            channel = discord.utils.get(ctx.guild.channels, id=club_channel)
        else:
            channel = None
        if channel:
            if action == "add":
                await member.add_roles(channel)
                return ctx.guild.get_member(discord_id)
            elif action == "remove":
                await member.remove_roles(channel)
                return ctx.guild.get_member(discord_id)
        return None

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return None
