import discord
import logfire
from discord.ext import commands

from src.database.db_models import User
from src.forms.rider_forms import RegistrationForm


class RiderCog(commands.Cog):
    """Rider related cogs."""

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @discord.slash_command()  # we can also add application commands
    async def rider_goodbye(self, ctx):
        """Say goodbye to the bot."""
        await ctx.respond("Goodbye!")

    @commands.Cog.listener()  # we can add event listeners to our cog
    async def on_member_join(self, member):
        """Triggered hen a member joins the server.

        - you must enable the proper intents
        - to access this event.
        - See the Popular-Topics/Intents page for more info
        """
        logfire.info(f"{member} joined the server!")
        await member.send("Welcome to the server!")

    @discord.slash_command()
    async def rider_lookup(self, ctx, user: discord.Member):
        """Look up a user in the registration database."""
        logfire.info(f"Looking up user: {user}")
        # rider = await Rider.find_one({"discord_id": user.id})
        user_profile = User.lookup(discord_id=user.id)

        if user_profile:
            logfire.info(f"Found user: {user_profile}")
            embed = discord.Embed(title="Registration Info", color=discord.Color.blue())
            embed.add_field(name="Discord", value=user.mention, inline=True)
            for k, v in user_profile.items():
                embed.add_field(name=k, value=v, inline=True)
            await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx.response.send_message("User not found in registration database.", ephemeral=True)

    @discord.slash_command(name="rider_register")
    async def rider_register(self, ctx):
        """Register a new rider. Press  enter: Only works in the '#rider-admin' channel."""
        if ctx.channel.name not in ["rider-admin", "bot-testing"]:
            await ctx.respond("This command can only be used in the `#rider-admin` channel.", ephemeral=True)
            logfire.warn(f"{ctx.author} tried to register outside of the rider-admin channel.")
            return
        INSTRUCTIONS = (
            'Welcome to Virtual Worlds racing "VWR"\n'
            "By registering, you agree to:\n"
            "- [Terms of Service, TOS.](https://example.com/terms)\n"
            "- [Privacy Policy, PP.](https://example.com/privacy)."
        )
        reg_view = RegistrationView()
        # await ctx.send(INSTRUCTIONS, view=reg_view, ephemeral=True)
        await ctx.response.send_message(INSTRUCTIONS, view=reg_view, ephemeral=True)


class RegistrationView(discord.ui.View):
    """A View that provides a button to show the Registration Form and displays instructions."""

    def __init__(self):
        super().__init__(timeout=300)  # Keeps the view active indefinitely until manually stopped

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
    bot.add_cog(RiderCog(bot))  # add the cog to the bot
