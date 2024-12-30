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

    ADMIN = "admin"
    REGISTERED = "registered"
    CLUB_MEMBER = "club_member"
    TEAM_MEMBER = "team_member"
    CLUB_ADMIN = "club_admin"
    TEAM_ADMIN = "team_admin"


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


async def check_role(
    ctx: discord.ext.commands.Context, discord_id: int, role_filter: BaseRole | Iterable[BaseRole]
) -> list[Role | None]:
    """List roles matching the provided filter term.

    Args:
        ctx (discord.ext.commands.Context): The context object.
        discord_id (int): The discord ID of the user to search for roles.
        role_filter (BaseRole | Iterable[BaseRole]): The role name to search for.

    """
    try:
        member = ctx.guild.get_member(discord_id)  # Get the member corresponding to discord_id

        # Filter roles based on the provided filter_term
        if isinstance(filter, BaseRole):
            filtered_roles = [role for role in member.roles if role.name == role_filter.value]
            return filtered_roles
        elif isinstance(filter, abc.Iterable):
            filtered_roles = [role for role in member.roles if role.name in [r.value for r in role_filter]]
            return filtered_roles
        else:
            return []

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return []  # Return an empty list in case of an error


async def add_base_role(
    ctx: discord.ext.commands.Context, discord_id: int, role_filter: BaseRole | Iterable[BaseRole]
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
        if isinstance(filter, BaseRole):
            role = discord.utils.get(ctx.guild.roles, name=role_filter.value)
            await member.add_roles(role)
            return ctx.guild.get_member(discord_id)
        elif isinstance(filter, abc.Iterable):
            for role_name in [r.value for r in role_filter]:
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                await member.add_roles(role)
                return ctx.guild.get_member(discord_id)

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return None


async def club_member_roles(
    ctx: discord.ext.commands.Context,
    discord_id: int,
    action: Literal["add", "remove"],
    channel: discord.channel | str | int | None,
) -> discord.Member | None:
    """Add or remove the discrod_id from the club channel role.

    Each club channel has a role with the same name as the channel.

    Args:
    ctx (discord.ext.commands.Context): The context object.
    discord_id (int): The discord ID of the user to search for roles.
    action (Literal["add", "remove"]): The action to perform.
    channel (discord.channel | str | int | None): The channel object or name or id of the channel.

    """
    try:
        member = ctx.guild.get_member(discord_id)  # Get the member corresponding to discord_id
        if isinstance(channel, str):
            channel = discord.utils.get(ctx.guild.channels, name=channel)
        elif isinstance(channel, int):
            channel = discord.utils.get(ctx.guild.channels, id=channel)

        if action == "add":
            await member.add_roles(channel)
            return ctx.guild.get_member(discord_id)
        elif action == "remove":
            await member.remove_roles(channel)
            return ctx.guild.get_member(discord_id)

    except Exception as exc:
        logfire.error(f"An error occurred: {exc}")
        return None
