"""Registration form implementation."""
import discord
from discord import ui, Interaction, Embed, Color
import logfire

from src.utils.imports import Rider

class RegistrationForm(ui.Modal, title="Virtual Worlds Racing Registration"):
    """Registration form for new riders."""
    
    def __init__(self):
        super().__init__()
        
        # Form fields
        self.name = ui.TextInput(
            label="Full Name",
            placeholder="Enter your name...",
            min_length=3,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.name)

        self.zwid = ui.TextInput(
            label="Zwift ID Number",
            placeholder="Enter your Zwift ID",
            min_length=1,
            max_length=20,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.zwid)

        self.tos = ui.TextInput(
            label='Confirm Agreement',
            placeholder='Type "YES" to confirm you agree to the Terms and Privacy Policy',
            min_length=3,
            max_length=3,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.tos)

    async def on_submit(self, interaction: Interaction):
        """Process the registration form submission."""
        try:
            # Rest of your code remains the same...
            pass
        except Exception as e:
            logfire.error(f"Registration error for {interaction.user}: {str(e)}")
            await interaction.response.send_message(
                "❌ An error occurred during registration. Please try again later.",
                ephemeral=True
            ) 