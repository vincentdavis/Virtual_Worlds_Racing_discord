import discord
import logfire

from src.cats_and_chans import create_on_guild
from src.database.db_models import NewOrgMessage, Org


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
        else:
            self.zp_club_id = None

    async def callback(self, interaction: discord.Interaction):
        """Process the registration form."""
        logfire.info(f"Processing registration form for {interaction.user}")

        # Check if the club name already exists.
        try:
            zp_id = self.zp_club_id.value if self.zp_club_id is not None else None
            logfire.info("Creating Org object")
            new_org, message = await Org.new_org(
                discord_id=interaction.user.id,
                org_type=self.org_type,
                name=self.name.value,
                zp_club_id=zp_id,
            )

            logfire.info(f"New org and admin status: {message}")
            if message == NewOrgMessage.DUPLICATE:
                await interaction.respond(f"❌ Club '{self.name.value}' already exists.", ephemeral=True)
                return
            if message == NewOrgMessage.ERROR:
                logfire.warn("Org already Failed")
                await interaction.respond(f"❌ Club '{self.name.value}' failed", ephemeral=True)
                return

            # Get the rider making the request so that they can be added as an admin
            # rider = await Rider.find_one({"discord_id": interaction.user.id})
            # zp_id = self.zp_club_id.value if self.zp_club_id is not None else None
            # await Org(org_type=self.org_type, name=self.name.value, zp_club_id=zp_id, active=True).save()
            # new_org = await Org.find_one({"name": self.name.value})  # The name is unique

            # mem_type: MembType = MembType.CLUB_ADMIN if self.org_type == "club" else MembType.TEAM_ADMIN
            # logfire.info(f"New Org: {new_org}")
            # await Membership.add_remove_membership(
            #     action="add", rider=rider, org_id=new_org.id, membership_type=mem_type
            # )

            await interaction.respond(f"Org '{self.name.value}' successfully created!", ephemeral=True)
            # Wait for the form response
            await create_on_guild(self.ctx, self.org_type, self.name.value)
        except ValueError as e:
            await interaction.respond(f"❌ Error: {e!s}", ephemeral=True)
            logfire.error(f"Failed to create club: {e}")
        except Exception as e:
            logfire.error(f"Failed to create club: {e}")
            # raise e
            await interaction.respond(f"❌ Failed to create club. Unknown error.\n{e!s}", ephemeral=True)
