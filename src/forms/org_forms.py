import discord
import logfire

from src.cats_and_chans import create_on_guild
from src.database.db_models import User
from src.vwr_exceptions import UserNotRegistered


class CreateOrgForm(discord.ui.Modal):
    """Create Organization (Club or Team)."""

    def __init__(self, ctx, org_type) -> None:
        super().__init__(title="Create Organization (Club or Team)")
        self.ctx = ctx
        self.org_type = org_type
        # Display instructions at the top
        self.name = discord.ui.InputText(
            label=f"{org_type.upper()} Name",
            placeholder=f"Enter {org_type} name",
            min_length=3,
            max_length=50,
            required=True,
        )
        self.add_item(self.name)
        if org_type == "club":
            self.zp_club_id = discord.ui.InputText(
                label="ZwiftPower club id (optional)",
                placeholder="find a zp club page",
                min_length=1,
                max_length=20,
                required=True,
            )
            self.add_item(self.zp_club_id)
            self.discord_server_id = discord.ui.InputText(
                label="Club Discord server id",
                placeholder="0123456789",
                min_length=10,
                max_length=100,
                required=False,
            )
            self.add_item(self.discord_server_id)
            self.website = discord.ui.InputText(
                label="Club website",
                placeholder="https://MyClub.com",
                min_length=10,
                max_length=100,
                required=False,
            )
            self.add_item(self.website)
        else:
            self.zp_club_id = None
            self.discord_server_id = None
            self.website = None

    async def callback(self, interaction: discord.Interaction):
        """Process the registration form."""
        logfire.info(f"Processing registration form for {interaction.user}")

        # Get the user requesting
        user = User.get_or_none(User.discord_id == interaction.user.id)
        try:
            zp_id = self.zp_club_id.value if self.zp_club_id is not None else None
            logfire.info("Creating Org object")
            if self.org_type == "club":
                new_org = user.create_club(
                    discord_id=interaction.user.id,
                    club_name=self.name.value,
                    zp_club_id=zp_id,
                )
            elif self.org_type == "team":
                new_org = user.create_team(
                    discord_id=interaction.user.id,
                    name=self.name.value,
                )
        except UserNotRegistered as e:
            logfire.error(f"Failed to create club: {e}")
            await interaction.respond(
                f"❌ User '{self.name.value}' must be registered to create a Club or Team", ephemeral=True
            )
        except Exception as e:
            logfire.error(f"Failed to create {self.org_type}: {e}")
            await interaction.respond(f"❌ Failed to create {self.org_type}. Unknown error.\n{e!s}", ephemeral=True)

        await interaction.respond(f"{self.org_type.upper()} '{self.name.value}' successfully created!", ephemeral=True)
        # Wait for the form response
        try:
            await create_on_guild(self.ctx, self.org_type, self.name.value)
        except Exception as e:
            logfire.error(f"Failed to create club channel: {e}")
            # raise e
            await interaction.respond(f"❌ Failed to create club channel. Unknown error.\n{e!s}", ephemeral=True)
