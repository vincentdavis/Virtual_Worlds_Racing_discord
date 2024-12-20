"""Club related commands."""
import discord
from discord import app_commands
from discord.ext import commands
import logfire

from src.utils.imports import Club
from src.forms.club import ClubForm

class ClubCog(commands.Cog):
    """Cog handling club-related commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.allowed_channels = ["club-admin", "bot-testing"]

    @app_commands.command(
        name="create-club",
        description="Create a new club"
    )
    async def create_club(self, interaction: discord.Interaction):
        """Create a new club."""
        if not await self._check_channel(interaction):
            return
        
        try:
            # Create embed with instructions
            embed = discord.Embed(
                title="Create a New Club",
                description=(
                    "Welcome! Please read the instructions below before creating a club.\n\n"
                    "**Requirements:**\n"
                    "1. Club Name (3-50 characters)\n"
                    "2. Club Description (10-1000 characters)\n\n"
                    "Click 'Create Club' to start."
                ),
                color=discord.Color.blue()
            )
            
            # Create button to show form
            class CreateClubButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(
                        label="Create Club",
                        style=discord.ButtonStyle.primary,
                        emoji="🏢"
                    )
                
                async def callback(self, button_interaction: discord.Interaction):
                    modal = ClubForm()
                    await button_interaction.response.send_modal(modal)
            
            # Create view with button
            view = discord.ui.View()
            view.add_item(CreateClubButton())
            
            # Send instructions with button
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )
            logfire.info(f"Sent club creation instructions to {interaction.user}")
            
        except Exception as e:
            logfire.error(f"Failed to start club creation: {str(e)}")
            await interaction.response.send_message(
                "❌ Failed to start club creation", 
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
    await bot.add_cog(ClubCog(bot)) 