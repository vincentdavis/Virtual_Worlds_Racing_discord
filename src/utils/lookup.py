"""User lookup functionality."""
from discord import Interaction, Embed, Color, Member
import logfire

from src.utils.imports import Rider

async def lookup_user(interaction: Interaction, user: Member):
    """Look up a user in the registration database."""
    logfire.info(f"Looking up user: {user}")
    
    try:
        rider = await Rider.find_one({"discord_id": user.id})
        if not rider:
            await interaction.response.send_message(
                "User not found in registration database.",
                ephemeral=True
            )
            return

        embed = Embed(title="Registration Info", color=Color.blue())
        embed.add_field(name="Discord", value=user.mention, inline=True)
        embed.add_field(name="Name", value=rider.name, inline=True)
        embed.add_field(name="Zwift ID", value=str(rider.zwid), inline=True)
        
        # Add profile links
        embed.add_field(
            name="ZwiftPower Profile",
            value=f"[View Profile](https://zwiftpower.com/profile.php?z={rider.zwid})",
            inline=True
        )
        embed.add_field(
            name="ZwiftRacing Profile",
            value=f"[View Profile](https://www.zwiftracing.app/riders/{rider.zwid})",
            inline=True
        )
        
        # Add registration date if available
        if hasattr(rider, 'created_at'):
            embed.add_field(
                name="Registered",
                value=rider.created_at.strftime("%Y-%m-%d"),
                inline=True
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logfire.info(f"Successfully looked up user: {user}")
        
    except Exception as e:
        logfire.error(f"Error looking up user {user}: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while looking up the user.",
            ephemeral=True
        ) 