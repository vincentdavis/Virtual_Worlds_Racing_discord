"""Rider related commands."""
import discord
from discord import app_commands
from discord.ext import commands
import logfire

from src.utils.imports import RegistrationForm, lookup_user

class RiderCog(commands.Cog):
    """Cog handling rider-related commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.allowed_channels = ["rider-admin", "bot-testing"]

    @app_commands.command(
        name="register",
        description="Register as a new rider with your Zwift details"
    )
    async def register(self, interaction: discord.Interaction):
        """Register a new rider."""
        if not await self._check_channel(interaction):
            return
        
        try:
            # Create embed with instructions and clickable links
            embed = discord.Embed(
                title="Virtual Worlds Racing Registration",
                description=(
                    "Welcome! Please read the instructions below before registering.\n\n"
                    "**Registration Requirements:**\n"
                    "1. Full Name (minimum 3 characters)\n"
                    "2. Zwift ID (numeric identifier)\n\n"
                    "**Important Links:**\n"
                    "• [Terms of Service](https://example.com/terms)\n"
                    "• [Privacy Policy](https://example.com/privacy)\n\n"
                    "By clicking 'Start Registration', you acknowledge that you have read and agree to our Terms of Service and Privacy Policy."
                ),
                color=discord.Color.blue()
            )
            
            # Create button to show form
            class RegisterButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(
                        label="Start Registration",
                        style=discord.ButtonStyle.primary,
                        emoji="📝"
                    )
                
                async def callback(self, button_interaction: discord.Interaction):
                    modal = RegistrationForm()
                    await button_interaction.response.send_modal(modal)
            
            # Create view with button
            view = discord.ui.View()
            view.add_item(RegisterButton())
            
            # Send instructions with button
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )
            logfire.info(f"Sent registration instructions to {interaction.user}")
            
        except Exception as e:
            logfire.error(f"Failed to start registration: {str(e)}")
            await interaction.response.send_message(
                "❌ Failed to start registration", 
                ephemeral=True
            )

    @app_commands.command(
        name="lookup",
        description="Look up a registered rider's information"
    )
    async def lookup(self, interaction: discord.Interaction, user: discord.Member):
        """Look up a user in the registration database."""
        try:
            await lookup_user(interaction, user)
        except Exception as e:
            logfire.error(f"Failed to lookup user: {str(e)}")
            await interaction.response.send_message(
                "❌ Failed to lookup user", 
                ephemeral=True
            )

    async def _check_channel(self, interaction: discord.Interaction) -> bool:
        """Check if command is used in allowed channel."""
        if interaction.channel.name not in self.allowed_channels:
            logfire.warn(f"{interaction.user} tried to use command in wrong channel")
            await interaction.response.send_message(
                f"This command can only be used in: {', '.join(self.allowed_channels)}",
                ephemeral=True
            )
            return False
        return True

async def setup(bot: commands.Bot):
    """Set up the cog."""
    await bot.add_cog(RiderCog(bot)) 