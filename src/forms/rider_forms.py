import discord
import logfire

from src.database.db_models import User
from src.extras.roles_mgnt import BaseRole, add_base_role


class RegistrationForm(discord.ui.Modal):
    """Registration form."""

    def __init__(self) -> None:
        super().__init__(title="Registration Form")

        self.name = discord.ui.InputText(
            label="Full Name", placeholder="Enter your name...", min_length=3, max_length=50, required=True
        )
        self.add_item(self.name)

        self.zwid = discord.ui.InputText(
            label="Zwift ID Number", placeholder="Enter your Zwift ID", min_length=1, max_length=50, required=True
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
                # NOTE: We don't need to do this because we check on the slah command for the role
                existing_discord = User.get_or_none(User.discord_id == interaction.user.id)
                if existing_discord:
                    await interaction.response.send_message(
                        "❌ You are already registered a Contact an admin if there are problems", ephemeral=True
                    )
                    logfire.warn(f"{interaction.user} tried to register again.")
                    return

                existing_zwid = User.get_or_none(User.zwid == zwid_int)
                if existing_zwid:
                    await interaction.response.send_message(
                        "❌ Zwift ID is already registered! Contact an admin if there are problems", ephemeral=True
                    )
                    logfire.warn(f"{interaction.user} tried to register with an existing Zwift ID.")

                existing_name = User.get_or_none(User.name == self.name.value)
                if existing_name:
                    await interaction.response.send_message(
                        "❌ Name is already registered! Contact an admin if there are problems", ephemeral=True
                    )
                    logfire.warn(f"{interaction.user} tried to register a existing name again.")
                    return
            except Exception as e:
                logfire.error(f"Failed to check for user already exists: {e}")
                await interaction.response.send_message("❌ Failed to check for user already exists", ephemeral=True)
                return

            try:
                # Create and save registration
                logfire.info(f"Saving {interaction.user} with zwid {zwid_int}")
                user_def = dict(
                    discord_id=interaction.user.id,
                    discord_name=str(interaction.user),
                    name=self.name.value,
                    zwid=zwid_int,
                    tos=tos,
                    active=True,
                )
                logfire.info(f"Creating User object with:\n {user_def}")
                user = User.create(
                    discord_id=interaction.user.id,
                    discord_name=str(interaction.user),
                    name=self.name.value,
                    zwid=zwid_int,
                    tos=tos,
                    active=True,
                )
                await add_base_role(interaction, interaction.user.id, BaseRole.REGISTERED)
                # Send confirmation
                # TODO: Sould send the rider lookup view
                logfire.info(f"Sending confirmation to {interaction.user}")
                embed = discord.Embed(title="✅ Registration Successful!", color=discord.Color.green())
                embed.add_field(name="Name", value=self.name.value, inline=True)
                embed.add_field(name="Zwift ID", value=self.zwid.value, inline=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)

                # Log registration
                logfire.info(f"Logging registration for {interaction.user}")
                log_channel = discord.utils.get(interaction.guild.channels, name="activity_logs")
                if log_channel:
                    await log_channel.send(embed=embed)

            except ValueError:
                await interaction.response.send_message("❌ Zwift ID be a valid number.", ephemeral=True)
                logfire.error(f"{interaction.user} entered an invalid Zwift ID.")

            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to register user: {user_def}.", ephemeral=True)
                logfire.error(f"Failed to register user: {user_def}\n {e}", exc_info=True)

            logfire.info(f"Registration complete for {interaction.user}")
