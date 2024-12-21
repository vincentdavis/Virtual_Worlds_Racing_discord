import discord
import logfire

from src.database.db_models import Club, Rider


class ClubForm(discord.ui.Modal):
    """Registration form."""

    def __init__(self) -> None:
        super().__init__(title="Create Club")
        # Display instructions at the top

        self.name = discord.ui.InputText(
            label="Club Name", placeholder="Enter club name", min_length=3, max_length=50, required=True
        )
        self.add_item(self.name)

        self.zp_club_id = discord.ui.InputText(
            label="ZwiftPower club id (optional)",
            placeholder="find a zp club page",
            min_length=1,
            max_length=20,
            required=True,
        )
        self.add_item(self.zp_club_id)

    async def callback(self, interaction: discord.Interaction):
        """Process the registration form."""
        logfire.info(f"Processing registration form for {interaction.user}")
        try:
            club_exists = await Club.find_one({"name": self.name.value})
            if club_exists:
                logfire.warn("Club already exists")
                await interaction.respond(f"❌ Club '{self.name.value}' already exists.", ephemeral=True)
                return
            logfire.info("Creating club object")
            rider = await Rider.find_one({"discord_id": interaction.user.id})
            await Club(name=self.name.value, zp_club_id=self.zp_club_id.value, admins=[rider]).save()
            await interaction.respond(f"Club '{self.name.value}' successfully created!", ephemeral=True)
        except ValueError as e:
            await interaction.respond(f"❌ Error: {e!s}", ephemeral=True)
            logfire.error(f"Failed to create club: {e}")
        except Exception as e:
            logfire.error(f"Failed to create club: {e}")
            await interaction.respond(f"❌ Failed to create club. Unknown error.\n{e!s}", ephemeral=True)
