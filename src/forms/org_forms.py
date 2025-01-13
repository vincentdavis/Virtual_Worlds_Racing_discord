import re

import discord
import logfire

from src.database.db_models import User
from src.extras.channel_mgnt import create_on_guild
from src.extras.roles_mgnt import BaseRole, add_base_role
from src.extras.vwr_exceptions import UserNotRegistered


class CreateOrgForm(discord.ui.Modal):
    """Create Organization (Club or Team)."""

    def __init__(self, ctx, org_type) -> None:
        super().__init__(title=f"Create or edit {org_type}")
        self.ctx = ctx
        self.org_type = org_type

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
                required=False,
            )
            self.add_item(self.zp_club_id)
            self.discord_server_id = discord.ui.InputText(
                label="Club Discord server id (optional)",
                placeholder="0123456789",
                min_length=10,
                max_length=100,
                required=False,
            )
            self.add_item(self.discord_server_id)
            self.website = discord.ui.InputText(
                label="Club website (optional)",
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
            logfire.info(f"Creating {self.org_type} object")
            if self.org_type == "club":
                new_org = user.create_club(
                    club_name=self.name.value,
                    zp_club_id=zp_id,
                )
            elif self.org_type == "team":
                new_org = user.create_team(
                    team_name=self.name.value,
                )
        except UserNotRegistered as e: # Double-check the user is registered in the db
            logfire.error(f"Failed to create {self.org_type}: {e}")
            await interaction.respond(
                f"❌ User '{self.name.value}' must be registered to create a Club or Team", ephemeral=True
            )
        except Exception as e:
            logfire.error(f"Failed to create {self.org_type}: {e}")
            await interaction.respond(f"❌ Failed to create {self.org_type}. Unknown error.\n{e!s}", ephemeral=True)

        await interaction.respond(f"{self.org_type.upper()} '{self.name.value}' successfully created!", ephemeral=True)

        # Setup channels and roles
        try:
            logfire.info(f"Create {self.name.value} channel in {self.org_type}")
            org_name = re.sub(r"[^a-z0-9_\-]", "-", self.name.value.lower())
            # Truncate name if it's too long (Discord limit is 100 characters)
            org_name = org_name[:100]
            new_channel = await create_on_guild(self.ctx, self.org_type, org_name)
            # Give the user the role of CLUB_MEMBER and CLUB_ADMIN
            if self.org_type == "club":
                await add_base_role(interaction, interaction.user.id, BaseRole.CLUB_MEMBER)
                await add_base_role(interaction, interaction.user.id, BaseRole.CLUB_ADMIN)
                logfire.info(f"Added {BaseRole.CLUB_MEMBER} and {BaseRole.CLUB_ADMIN} to {interaction.user}")
            if self.org_type == "team":
                await add_base_role(interaction, interaction.user.id, BaseRole.TEAM_MEMBER)
                await add_base_role(interaction, interaction.user.id, BaseRole.TEAM_ADMIN)
                logfire.info(f"Added {BaseRole.TEAM_MEMBER} and {BaseRole.TEAM_ADMIN} to {interaction.user}")

            logfire.info(f"Logging registration for {interaction.user}")
            log_channel = discord.utils.get(interaction.guild.channels, name="activity_logs")
            if log_channel:
                await log_channel.send(f"{interaction.user} created {self.org_type} '{new_channel.name}'")
        except Exception as e:
            logfire.error(f"General error, Failed to create {self.org_type.upper()} channel: {e}", exc_info=True)
            # raise e
            await interaction.respond(
                f"❌ Failed to create {self.org_type.upper()} channel. Unknown error.\n{e!s}", ephemeral=True
            )
