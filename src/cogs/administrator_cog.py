import logfire
from discord import slash_command
from discord.ext import commands


class AdminCog(commands.Cog):
    """Admin related cogs."""

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @slash_command(name="list_roles")
    async def list_roles(self, ctx):
        """List all roles and their permissions in the guild."""
        try:
            guild = ctx.guild
            logfire.info(f"Listing roles and permissions for guild {guild.name}.")
            # roles_data = {}
            # for role in guild.roles[0]:
            #     roles_data[role.name] = {perm: value for perm, value in role.permissions}
            await ctx.send(f"Roles and Permissions: {guild.roles}")
        except Exception as e:
            logfire.error(f"Failed to list roles and permissions: {e}")
            await ctx.send("❌ Failed to list roles and permissions.")


def setup(bot):
    """Pycord calls to setup the cog."""
    bot.add_cog(AdminCog(bot))  # add the cog to the bot
