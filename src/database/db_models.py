from datetime import datetime

import logfire
from beanie import Document, Link
from pydantic import Field


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

    class Settings:
        """Settings for the document."""

        name = "riders"
        # indexes = [("discord_id", 1), ("zwid", 1)]


class Team(Document):
    """Team document model."""

    name: str = Field(min_length=3, max_length=50)
    admins: list[Link[Rider]] = Field(min_length=1)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    async def save(self, *args, **kwargs) -> None:
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        await super().save(*args, **kwargs)

    class Settings:
        """Settings for the document."""

        name = "teams"
        # indexes = [{"fields": ["name"], "unique": True}]


class Club(Document):
    """Club document model."""

    # TODO: Should do some checking on the class methods to be sure the user is an admin
    name: str = Field(min_length=3, max_length=50)
    zp_club_id: int | None = None  # Optional Zwift Power team (club) id
    admins: list[Link[Rider]] = Field(min_length=1)
    teams: list[Link[Team]] | None = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    async def save(self, *args, **kwargs) -> None:
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        await super().save(*args, **kwargs)

    async def mark_active(self):
        """Mark the club as active."""
        self.active = True
        await self.save()

    async def mark_inactive(self):
        """Mark the club as inactive."""
        self.active = False
        await self.save()

    async def add_admin(self, rider: "Rider") -> None:
        """Add a new admin to the club."""
        if rider not in self.admins:
            self.admins.append(Link(rider))
            await self.save()

    async def remove_admin(self, rider: "Rider") -> None:
        """Remove an admin from the club."""
        if rider in self.admins:
            if len(self.admins) == 1:
                raise ValueError("A club must have at least one admin.")
            self.admins.remove(Link(rider))
            await self.save()

    async def add_team(self, team: "Team") -> None:
        """Add a team to the club."""
        if self.teams is None:
            self.teams = []
        if team not in self.teams:
            self.teams.append(Link(team))
            await self.save()

    async def remove_team(self, team: "Team") -> None:
        """Remove a team from the club."""
        if self.teams and team in self.teams:
            self.teams.remove(Link(team))
            await self.save()

    @classmethod
    async def create_club(cls, name: str, creator: Rider, zp_club_id: int | None = None) -> "Club":
        """Create a new club and assign the creator as an admin.

        Args:
            name: The name of the club
            creator: The rider creating the club
            zp_club_id: Optional Zwift Power club ID

        Returns:
            The newly created club

        Raises:
            ValueError: If the creator is inactive

        """
        try:
            logfire.info(f"Saving club'{name}'")
            creator = await Rider.find_one({"discord_id": creator.discord_id})
            if not creator.active:
                logfire.error(f"Rider {creator.name} is inactive")
                return None
            club = cls(name=name, zp_club_id=zp_club_id, admins=[creator])
            await club.save()
            return club
        except Exception as e:
            logfire.error(f"Failed to create club: {e}")
            raise e

    class Settings:
        name = "clubs"
        # indexes = [
        #     {"key": [("name", 1)]},
        #     {"key": [("zp_club_id", 1)]},
        # ]
