"""Registration form."""

import discord
import discord as pycord
import logfire

# from discord.ext import commands
from dotenv import load_dotenv

from db_models import Rider

load_dotenv()


# Discord bot setup
# bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


class RegistrationForm(discord.ui.Modal):
    """Registration form."""

    def __init__(self) -> None:
        super().__init__(title="Registration Form")
        # Display instructions at the top

        self.name = discord.ui.InputText(
            label="Full Name", placeholder="Enter your name...", min_length=3, max_length=50, required=True
        )
        self.add_item(self.name)

        self.zwid = discord.ui.InputText(
            label="Zwift ID Number", placeholder="Enter your Zwift ID", min_length=1, max_length=20, required=True
        )
        self.add_item(self.zwid)

        self.tos = discord.ui.InputText(
            label='I agree to TOS. and PP. type "YES"',
            placeholder='Enter "YES"',
            min_length=3,
            max_length=3,
            required=True,
        )
        self.add_item(self.tos)

    async def callback(self, interaction: discord.Interaction):
        """Process the registration form."""
        with logfire.span("Creating new Rider/User"):
            logfire.info(f"Processing registration form for {interaction.user}")
            try:
                if self.tos.value.lower() != "yes":
                    await interaction.response.send_message(
                        "❌ You must agree to the TOS. and PP. to register. Please try again or go away ;-)",
                        ephemeral=True,
                    )
                    logfire.warn(f"{interaction.user} did not agree to TOS. and PP.")
                    return
                else:
                    logfire.info(f"{interaction.user} agreed to TOS. and PP.")
                    tos = True
                zwid_int = int(self.zwid.value)
                # Check if user is already registered
                existing_discord = await Rider.find_one({"discord_id": interaction.user.id})
                if existing_discord:
                    await interaction.response.send_message(
                        "❌ You are already registered a Contact an admin if there are problems", ephemeral=True
                    )
                    logfire.warn(f"{interaction.user} tried to register again.")
                    return

                existing_zwid = await Rider.find_one({"zwid": zwid_int})
                if existing_zwid:
                    await interaction.response.send_message(
                        "❌ Zwift ID is already registered! Contact an admin if there are problems", ephemeral=True
                    )
                    logfire.warn(f"{interaction.user} tried to register with an existing Zwift ID.")
                existing_name = await Rider.find_one({"name": self.name.value})
                if existing_name:
                    await interaction.response.send_message(
                        "❌ Name is already registered! Contact an admin if there are problems", ephemeral=True
                    )
                    logfire.warn(f"{interaction.user} tried to register a existing name again.")
                    return
            except Exception as e:
                logfire.error(f"Failed to check for user already exists: {e}")
                await interaction.response.send_message("❌ Failed to check for user already exists", ephemeral=True)

            try:
                # Create and save registration
                logfire.info(f"Saving {interaction.user} with zwid {zwid_int}")
                rider = Rider(
                    discord_id=interaction.user.id,
                    discord_name=str(interaction.user),
                    name=self.name.value,
                    zwid=zwid_int,
                    tos=tos,
                )
                await rider.save()

                # Send confirmation
                logfire.info(f"Sending confirmation to {interaction.user}")
                embed = discord.Embed(title="✅ Registration Successful!", color=discord.Color.green())
                embed.add_field(name="Name", value=self.name.value, inline=True)
                embed.add_field(name="Zwift ID", value=self.zwid.value, inline=True)

                await interaction.response.send_message(embed=embed, ephemeral=True)

                # Log registration
                logfire.info(f"Logging registration for {interaction.user}")
                log_channel = discord.utils.get(interaction.guild.channels, name="registrations")
                if log_channel:
                    await log_channel.send(f"New registration: {interaction.user.mention}")

            except ValueError:
                await interaction.response.send_message("❌ Zwift ID be a valid number.", ephemeral=True)
                logfire.error(f"{interaction.user} entered an invalid Zwift ID.")
            logfire.info(f"Registration complete for {interaction.user}")


async def lookup_user(ctx, user: pycord.Member):
    """Look up a user in the registration database."""
    logfire.info(f"Looking up user: {user}")
    rider = await Rider.find_one({"discord_id": user.id})
    if rider:
        logfire.info(f"Found user: {rider}")
        embed = pycord.Embed(title="Registration Info", color=pycord.Color.blue())
        embed.add_field(name="Discord", value=user.mention, inline=True)
        embed.add_field(name="Name", value=rider.name, inline=True)
        embed.add_field(name="Zwift ID", value=str(rider.zwid), inline=True)
        embed.add_field(
            name="ZwiftPower Profile",
            value=f"[View Profile](https://zwiftpower.com/profile.php?z={rider.zwid})",
            inline=True,
        )
        embed.add_field(
            name="ZwiftRacing Profile",
            value=f"[View Profile](https://www.zwiftracing.app/riders/{rider.zwid})",
            inline=True,
        )

        embed.add_field(name="Registered", value=rider.created_at.strftime("%Y-%m-%d"), inline=True)

        await ctx.response.send_message(embed=embed, ephemeral=True)
    else:
        await ctx.response.send_message("User not found in registration database.", ephemeral=True)


class RegistrationView(discord.ui.View):
    """A View that provides a button to show the Registration Form and displays instructions."""

    def __init__(self):
        super().__init__(timeout=None)  # Keeps the view active indefinitely until manually stopped

        # # Add the registration button
        # self.add_item(discord.ui.Button(label="Cancel", style=discord.ButtonStyle.primary, custom_id="Cancel"))

    @discord.ui.button(label="Register Now", style=discord.ButtonStyle.primary)
    async def register_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Display the registration modal."""
        logfire.info(f"{interaction.user} clicked Register Now")
        modal = RegistrationForm()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.primary)
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Do nothing"""
        logfire.info(f"{interaction.user} cancelled registration")
        await interaction.response.send_message("Registration cancelled", ephemeral=True)
