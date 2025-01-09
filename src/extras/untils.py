"""Utility functions for the project."""
import discord
import logfire
import discord.ext.commands

# async def is_registered(ctx, fail_message: str = "You must be a registered rider to perform this action."):
#     """Check if a rider is registered."""
#     try:
#         logfire.info(f"Checking if user {ctx.author} is a registered rider.")
#         rider = await Rider.find_one({"discord_id": ctx.author.id})
#         if not rider:
#             logfire.info(f"User {ctx.author} is not a registered rider.")
#             await ctx.response.send_message(fail_message, ephemeral=True)
#             return False
#         return True
#     except Exception as e:
#         logfire.error(f"Failed to check if user is registered: {e}")
#         await ctx.response.send_message("❌ Failed to check if user is registered.", ephemeral=True)
#         return False


async def check_channel(ctx, channel_names: list, fail_message: str):
    """Check if the command is being run in the correct channel."""
    try:
        logfire.info("Checking if command is being run in the correct channel.")
        check_in = [*channel_names, "bot-testing"]
        if ctx.channel.name not in check_in:
            await ctx.response.send_message(fail_message, ephemeral=True)
            logfire.warn(f"{ctx.author} tried to run a command outside of the {channel_names} channel.")
            return False
        return True
    except Exception as e:
        logfire.error(f"Failed to check channel: {e}")
        await ctx.response.send_message("❌ Failed to check channel.", ephemeral=True)
        return False

def check_role(ctx:discord.ext.commands.Context, role:str):
    """Check that the user has a role, used to restrict slash commands"""
    has_role = role in [role.name for role in ctx.author.roles]
    return has_role

