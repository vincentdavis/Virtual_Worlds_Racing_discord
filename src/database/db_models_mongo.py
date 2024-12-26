from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

import logfire
from beanie import Document
from bson import ObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class MembType(Enum):  # NOQA
    CLUB_ADMIN = "club_admin"
    TEAM_ADMIN = "team_admin"
    TEAM_MEMBER = "team_member"
    CLUB_MEMBER = "club_member"


class NewOrgMessage(Enum):  # NOQA
    SUCCESS = "success"
    DUPLICATE = "duplicate"
    ERROR = "error"


class Rider(Document):
    """Rider document model."""

    name: str = Field(min_length=3, max_length=50)
    zwid: int = Field(gt=0)
    discord_id: int = Field(gt=0)
    discord_name: str
    tos: bool = Field(default=False)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    async def save(self, *args, **kwargs):
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        await super().save(*args, **kwargs)

    @classmethod
    async def is_registered(cls, ctx, fail_message: str = "You must be a registered rider to perform this action."):
        """Check if a rider is registered."""
        try:
            logfire.info(f"Checking if user {ctx.author} is a registered rider.")
            rider = await cls.find_one({"discord_id": ctx.author.id})
            if not rider:
                logfire.info(f"User {ctx.author} is not a registered rider.")
                await ctx.response.send_message(fail_message, ephemeral=True)
                return False
            return True
        except Exception as e:
            logfire.error(f"Failed to check if user is registered: {e}")
            await ctx.response.send_message("❌ Failed to check if user is registered.", ephemeral=True)
            return False

    class Settings:  # NOQA
        name = "riders"
        indexes = [  # noqa: RUF012
            IndexModel([("name", ASCENDING)], unique=True),
            IndexModel([("zwid", ASCENDING)], unique=True),
            IndexModel([("discord_id", ASCENDING)], unique=True),
        ]


class Org(Document):
    """Club and team and other model."""

    org_type: Literal["club", "team"]
    name: str = Field(min_length=3, max_length=50)
    discord_id: str | None = None  # Discord id of the user that created the club
    zp_club_id: int | None = None  # Optional Zwift Power team (club) id
    active: bool = True
    note: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    async def save(self, *args, **kwargs) -> None:
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        await super().save(*args, **kwargs)

    @classmethod
    async def new_org(
        cls, discord_id: int, org_type: Literal["club", "team"], name: str, zp_club_id: int | None = None
    ) -> tuple[Optional["Org"], NewOrgMessage]:
        """Create a new club or team."""
        with logfire.span("New Org"):
            existing_org = await cls.find_one({"name": name})
            if existing_org:
                logfire.info(f"Org already exists: {existing_org}")
                return (None, NewOrgMessage.DUPLICATE)
            try:
                org = cls.model_validate(
                    {"org_type": org_type, "name": name, "discord_id": str(discord_id), "zp_club_id": zp_club_id}
                )
            except Exception as e:
                logfire.error(f"Failed to validate new org: {e}")
                return None, NewOrgMessage.ERROR
            rider = await Rider.find_one({"discord_id": discord_id})
            mem_type: MembType = MembType.CLUB_ADMIN if org_type == "club" else MembType.TEAM_ADMIN

            #####
            try:
                await org.save()
                logfire.info("New ORG SAVED")
                new_org = await Org.find_one({"name": name})  # The name is unique
                logfire.info("Retrieve new Org")

                logfire.info(f"Add Membership for {rider} to {new_org}")
                await Membership.add_remove_membership(
                    action="add", rider=rider, org_id=str(new_org.id), membership_type=mem_type
                )
                return org, NewOrgMessage.SUCCESS
            except Exception:
                logfire.error("Failed to creat new org and admin", exc_info=True)
                return None, NewOrgMessage.ERROR

    class Settings:  # NOQA
        name = "orgs"
        indexes = [  # noqa: RUF012
            IndexModel([("name", ASCENDING)], unique=True),
            IndexModel([("zp_club_id", ASCENDING)], unique=True),
            IndexModel([("discord_id", ASCENDING)], unique=True),
        ]


class Membership(Document):
    """Membership records for clubs and teams.

    MembType = Literal["club_admin", "team_admin", "team_member", "club_member"]
    """

    membership_type: MembType
    org_id: str
    rider_id: str
    discord_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    async def save(self, *args, **kwargs) -> None:  # NOQA
        self.updated_at = datetime.now()
        await super().save(*args, **kwargs)

    @classmethod
    async def get_user_membership(
        cls,
        membership_type: set[MembType],
        discord_id: int | None = None,
        rider_id: str | None = None,
        rider: Rider | None = None,
    ) -> list[Org | None]:
        """Find all clubs where the given user (discord_id or rider_id or Rider) is an admin."""
        try:
            if rider is not None:
                discord_id = str(rider.discord_id)
                rider_id = str(rider.id)
            logfire.info(f"Get Membership Orgs for user: {membership_type}, {discord_id}, {rider_id}, {rider}")
            query_filter = {
                "$or": [{"discord_id": discord_id}, {"rider_id": rider_id}],
                "membership_type": {"$in": list(membership_type)},
            }
            org_ids = [org.org_id for org in await cls.find(query_filter).to_list()]
            org_ids = [ObjectId(org_id) for org_id in org_ids]
            logfire.info(f"Membership Orgs: {org_ids}")
            orgs = await Org.find({"_id": {"$in": org_ids}}).to_list()
            logfire.info(f"Found user is a member if these orgs: {orgs}")
            return orgs
        except Exception as e:
            logfire.error(f"Failed to get user membership: {e}", exc_info=True)

    @classmethod
    async def add_remove_membership(
        cls,
        action: Literal["add", "remove"],
        membership_type: MembType,
        ctx: Any | None = None,
        org: Org | None = None,
        org_id: str | None = None,
        discord_id: int | None = None,
        rider_id: str | None = None,
        rider: Rider | None = None,
    ) -> Optional["Membership"]:
        """Add a new Club admin record."""
        with logfire.span("Add Membership"):
            # if not isinstance(discord_id, int) or discord_id <= 0:
            #     logfire.error(f"Invalid 'discord_id' provided. {discord_id}")
            #     raise ValueError("Invalid 'discord_id' provided.")
            if rider is not None:
                discord_id = rider.discord_id
                rider_id = rider.id
            if ctx is not None:  # noqa
                if not await Rider.is_registered(ctx):
                    return

            if not rider_id:
                rider_id = await Rider.find_one({"discord_id": discord_id})
                if not rider_id:
                    logfire.notice(f"Rider ID {discord_id} not found")
                    return

            if org is not None:
                org_id = org.id
            try:
                logfire.info(f"Prepare membership_obj for {membership_type}, {org_id}, {rider_id}, {discord_id}")
                new_mem_dict = {
                    "membership_type": membership_type,
                    "org_id": str(org_id),
                    "rider_id": str(rider_id),
                    "discord_id": int(discord_id),
                }
                new_membership = cls.model_validate(new_mem_dict)
            except Exception as e:
                logfire.error(f"Failed to validate membership object: {e!s}")
                logfire.error(f"Unexpected error: {e}", exc_info=True)
                return
            logfire.info("Check for existing membership")
            existing_membership = await cls.find(
                {
                    "$and": [
                        {"membership_type": membership_type},
                        {"org_id": str(org_id)},
                        {"rider_id": str(rider_id)},
                        {"discord_id": int(discord_id)},
                    ]
                }
            ).first_or_none()
            if existing_membership is not None:
                logfire.info(f"Membership exists for {membership_type}")
                existing_membership.membership_type = membership_type
                await existing_membership.save()
            else:
                logfire.info(f"Non found Adding membership for {new_membership}")
                await new_membership.save()
                return new_membership

    class Settings:  # NOQA
        name = "membership"
        indexes = [  # noqa: RUF012
            IndexModel(
                [("membership_type", ASCENDING), ("discord_id", ASCENDING), ("org_id", ASCENDING)],
                unique=True,
                name="unique_membership",
            )
        ]


###############
