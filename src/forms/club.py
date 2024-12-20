"""Club form implementation."""
import discord
from discord import ui, Interaction, Embed, Color
import logfire

from src.utils.imports import Club

class ClubForm(ui.Modal, title="Virtual Worlds Racing Club Registration"):
    """Club registration form."""
    
    def __init__(self):
        super().__init__()
        
        # Form fields
        self.name = ui.TextInput(
            label="Club Name",
            placeholder="Enter club name...",
            min_length=3,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.name)

        self.description = ui.TextInput(
            label="Club Description",
            placeholder="Enter club description...",
            min_length=10,
            max_length=1000,
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.description)

    async def on_submit(self, interaction: Interaction):
        """Process the club registration form submission."""
        try:
            # Check for existing club
            existing_club = await Club.find_one({"name": self.name.value})
            if existing_club:
                await interaction.response.send_message(
                    "❌ A club with this name already exists.",
                    ephemeral=True
                )
                return

            # Create new club
            club = Club(
                name=self.name.value,
                description=self.description.value,
                owner_id=interaction.user.id,
                owner_name=str(interaction.user)
            )
            await club.save()

            # Send confirmation
            embed = Embed(
                title="✅ Club Created Successfully!",
                color=Color.green()
            )
            embed.add_field(name="Name", value=self.name.value, inline=True)
            embed.add_field(name="Owner", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logfire.info(f"New club created: {self.name.value} by {interaction.user}")

        except Exception as e:
            logfire.error(f"Club creation error for {interaction.user}: {str(e)}")
            await interaction.response.send_message(
                "❌ An error occurred during club creation. Please try again later.",
                ephemeral=True
            ) 