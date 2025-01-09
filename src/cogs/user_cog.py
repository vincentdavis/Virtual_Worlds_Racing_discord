"""User related commands."""

import discord
import logfire
from discord import user_command
from discord.ext import commands

from src.database.db_models import User
from src.extras.roles_mgnt import BaseRole, check_user_roles
from src.extras.vwr_exceptions import UserNotRegistered
from src.forms.rider_forms import RegistrationForm


class UserCog(commands.Cog):
    """Rider related cogs."""

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    rider = discord.SlashCommandGroup("rider", "Rider management commands.")

    async def rider_lookup(self, ctx, rider: discord.Member):
        """Look up a Rider in the user registration database."""
        with logfire.span("RIDER LOOKUP"):
            try:
                logfire.info(f"Looking up rider: {rider}")
                # Check author role
                check, msg, roles = await check_user_roles(
                    ctx, discord_id=ctx.author.id, role_filter=BaseRole.REGISTERED
                )
                if not check:
                    await ctx.response.send_message(
                        f"Error: {msg}",
                        ephemeral=True,
                    )
                    return
                user_profile = User.lookup(discord_id=rider.id)
                if user_profile:
                    logfire.info(f"Found user: {user_profile}")
                    embed = discord.Embed(title="Registration Info", color=discord.Color.blue())
                    embed.add_field(name="Discord", value=rider.mention, inline=True)
                    for k, v in user_profile.items():
                        embed.add_field(name=k, value=v, inline=True)
                    rider_obj = ctx.guild.get_member(rider.id)
                    rider_roles = rider_obj.roles

                    embed.add_field(name="Roles", value=str(list(role.name for role in rider_roles)), inline=True)
                    await ctx.response.send_message(embed=embed, ephemeral=True)
                # else:
                #     await ctx.response.send_message(
                #         "Rider not found in Rider registration database. They probably need to register",
                #         ephemeral=True,
                #     )
            except UserNotRegistered as e:
                logfire.info(f"send message: Error: {rider} is not registered. They need to register. {e}")
                await ctx.response.send_message(
                    f"Error: {rider} is not registered. They need to register.",
                    ephemeral=True,
                )
            except Exception as e:
                logfire.error(f"Error looking up rider: {e}")
                await ctx.response.send_message("Error looking up rider.", ephemeral=True)

    @commands.Cog.listener()  # we can add event listeners to our cog
    async def on_member_join(self, member):
        """Triggered hen a member joins the server.

        - you must enable the proper intents
        - to access this event.
        - See the Popular-Topics/Intents page for more info
        """
        logfire.info(f"{member} joined the server!")
        await member.send('Welcome to the server! Please register using "register"')

    @user_command(name="profile", description="Get users profile.")
    async def rider_user_profile(self, ctx, user):
        """Get a Rider's profile. Press enter: Only works in the '#rider-admin' channel."""
        with logfire.span("RIDER PROFILE APP CMD"):
            logfire.info(f"{ctx.author} is trying to get a profile.")
            await self.rider_lookup(ctx, user)

    @rider.command(name="profile", description="Get a Riders profile. Select from the list or start to type a name.")
    async def rider_slash_profile(self, ctx, rider: discord.Member):
        """Get a Rider profile. Press enter."""
        with logfire.span("RIDER PROFILE SLASH CMD"):
            logfire.info(f"{ctx.author} is trying to get a profile.")
            await self.rider_lookup(ctx, rider)

    @rider.command(name="register", description="Register with VWR.")
    async def rider_register(self, ctx):
        """Register a new rider. Press  enter: Only works in the '#rider-admin' channel."""
        with logfire.span("RIDER REGISTER"):
            logfire.info(f"{ctx.author} is trying to register.")
            TOS_URL = "https://docs.google.com/document/d/1A_taMO8z1iPtLZr4s9KSMtpjwHvFuSNLZAhSVBkPkTk/edit?usp=sharing"
            PP_URL = "https://docs.google.com/document/d/1sG5ZKQVuKbKpVzJErriR9fo9aOJzAUDMER8Znqt6QuM/edit?usp=sharing"
            WEBSITE_URL = "https://sites.google.com/view/virtual-worlds-racing/home"
            INSTRUCTIONS = (
                "Welcome to Virtual Worlds racing VWR\n"
                "By registering, you agree to:\n"
                f"- [Terms of Service, TOS.]({TOS_URL})\n"
                f"- [Privacy Policy, PP.]({PP_URL})."
                f"- [Website LINK]{WEBSITE_URL})"
            )
            check, msg, roles = await check_user_roles(ctx, discord_id=ctx.author, role_filter=BaseRole.REGISTERED)
            if check:  # The user is already registered
                await ctx.response.send_message(
                    f"Error: {ctx.author} is already registered.",
                    ephemeral=True,
                )
            if ctx.channel.name not in ["welcome-and-rules", "bot-testing"]:
                await ctx.respond("This command can only be used in the `#rider-admin` channel.", ephemeral=True)
                logfire.warn(f"{ctx.author} tried to register outside of the rider-admin channel.")
                return

            reg_view = RegistrationView()
            # await ctx.send(INSTRUCTIONS, view=reg_view, ephemeral=True)
            await ctx.response.send_message(INSTRUCTIONS, view=reg_view, ephemeral=True)


class RegistrationView(discord.ui.View):
    """A View that provides a button to show the Registration Form."""

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Register Now", style=discord.ButtonStyle.primary)
    async def register_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Display the registration modal."""
        logfire.info(f"{interaction.user} clicked Register Now")
        modal = RegistrationForm()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.primary)
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Do nothing."""
        logfire.info(f"{interaction.user} cancelled registration")
        await interaction.response.send_message("Registration cancelled", ephemeral=True)


def setup(bot):
    """Pycord calls to setup the cog."""
    bot.add_cog(UserCog(bot))  # add the cog to the bot
