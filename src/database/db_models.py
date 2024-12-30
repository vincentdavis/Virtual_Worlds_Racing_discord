"""Peewee model definitions for the database."""

import os
from datetime import datetime

import logfire
from dotenv import load_dotenv
from peewee import (
    BigIntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    IntegrityError,
    Model,
    SqliteDatabase,
)
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict
from psycopg2 import OperationalError

from src.extras.vwr_exceptions import (
    NoClubMembership,
    NotAClubAdmin,
    NotATeamAdmin,
    TeamNotFound,
    UserAlreadyInClub,
    UserAlreadyOnTeam,
    UserNotRegistered,
)


def init_db():
    """Initialize the Peewee database."""
    try:
        load_dotenv()
        database_url = os.getenv("DATABASE_URL", None)
        if database_url is not None:
            logfire.info(f"Database URL: {database_url.split("@")[-1]}")
            db = connect(database_url)
            logfire.info("Connected to PostgreSQL database.")
            return db
        else:
            sqlite_file_name = "Peewee_SQLite.db"
            logfire.info(f"Database URL: {sqlite_file_name}")
            db = SqliteDatabase(sqlite_file_name)
            logfire.info("Connected to SQLite database.")
            return db
    except Exception as e:
        logfire.error(f"Failed to connect to the database: {e}", exc_info=True)
        raise e


db = init_db()


class BaseModel(Model):
    """Base model to define the database connection."""

    class Meta:  # noqa: D106
        database = db


class Club(BaseModel):
    """Club model."""

    name = CharField(unique=True, index=True, max_length=50)
    zp_club_id = IntegerField(null=True, unique=True)  # Optional Zwift Power team (club) ID
    website = CharField(null=True, unique=True)
    discord_id = CharField(null=False, unique=True)  # Discord ID of the user that created the club
    discord_server_id = BigIntegerField(null=True)  # Discord server ID like 1317875072089981022
    active = BooleanField(default=True)
    note = CharField(null=True)
    discord_channel_id = BigIntegerField(null=True)
    discord_role_id = BigIntegerField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)


class Team(BaseModel):
    """Team model."""

    name = CharField(unique=True, index=True, max_length=50)
    discord_id = CharField(null=False)  # Discord ID of the user that created the team
    active = BooleanField(default=True)
    note = CharField(null=True)
    club_id = ForeignKeyField(Club, backref="teams", null=True, on_delete="CASCADE")  # ForeignKey for club
    discord_channel_id = BigIntegerField(null=True)
    discord_role_id = BigIntegerField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

    @property
    def members(self, as_dict: bool = False):
        """Return all users that are members of this team."""
        users = User.select().where(User.team_id == self)
        if not as_dict:
            return users
        else:
            return [model_to_dict(user) for user in users]

    @property
    def admins(self, as_dict: bool = False):
        """Return all users that are members of this team."""
        admins = User.select().where(User.team_id == self and User.team_admin)
        if not as_dict:
            return admins
        else:
            return [model_to_dict(user) for user in admins]


class User(BaseModel):
    """User model for the database."""

    name = CharField(unique=True, null=False, max_length=50)
    zwid = IntegerField(unique=True, null=False)
    discord_id = BigIntegerField(unique=True, null=False, index=True)
    discord_name = CharField(unique=True)
    tos = BooleanField(default=False)
    active = BooleanField(default=True)
    club_id = ForeignKeyField(Club, backref="users", null=True, on_delete="SET NULL")
    club_admin = BooleanField(default=False)
    team_id = ForeignKeyField(Team, backref="users", null=True, on_delete="SET NULL")
    team_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """Override save to update timestamp."""
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

    def create_club(
        self,
        club_name: str,
        zp_club_id: int | None = None,
        website: str | None = None,
        discord_server_id: int | None = None,
        **kwargs,
    ) -> Club:
        """Create a new club and assign the current user as the club admin.

        :param club_name: Name of the club to be created.
        :param zp_club_id: Optional Zwift Power team (club) ID.
        :param website: Optional website for the club.
        :param discord_server_id: Optional Discord server ID.
        :param kwargs: Additional fields for the Club model.
        :return: The created Club object.
        """
        try:
            new_club = Club.create(
                name=club_name,
                discord_id=self.discord_id,
                zp_club_id=zp_club_id,
                website=website,
                discord_server_id=discord_server_id,
                **kwargs,
            )
            self.club_id = new_club
            self.club_admin = True
            self.save()
            return new_club
        except IntegrityError as e:
            logfire.error(f"Failed to create club: IntegrityError: {e}", exc_info=True)
            raise e

    def create_team(self, team_name: str, join: bool = False, **kwargs) -> Team:
        """Create a new team and assign the current user as the team admin.

        :param team_name: Name of the team to be created.
        :param join: Join the team as an admin.
        :param kwargs: Additional fields for the Team model.
        :return: The created Team object.
        """
        if self.club_id is None:
            logfire.error(f"User {self.name} does not belong to a club.")
            raise NoClubMembership("User must belong to a club to create a team.")

        if not self.club_admin:
            logfire.error(f"User {self.name} is not a club admin.")
            raise NotAClubAdmin("User must be a club admin to create a team.")
        try:
            new_team = Team.create(name=team_name, discord_id=self.discord_id, club_id=self.club_id, **kwargs)
            if join:
                self.team_id = new_team
                self.team_admin = True
                self.save()
            return new_team
        except IntegrityError as e:
            logfire.error(f"Failed to create team: IntegrityError: {e}", exc_info=True)
            raise e

    def add_user_to_club(self, discord_id: int):
        """Add a user to a club. The club you are an admin of."""
        if not self.club_admin:
            logfire.error(f"User {self.name} is not a club admin.")
            raise NotAClubAdmin("User must be a club admin to create a team.")

        user = User.get_or_none(discord_id=discord_id)
        if user is None:
            logfire.error(f"User with Discord ID {discord_id} not found.")
            raise UserNotRegistered("Discord user needs to register")
        if user.club is not None:
            logfire.error(f"User {user.name} is already in a club.")
            raise UserAlreadyInClub("Discord user already in a club")
        user.club_id = self.club_id
        user.save()
        logfire.info(f"User {user.name} added to club {self.club_id}.")

    def add_user_to_team(self, discord_id: int, team_name: str | None = None):
        """Add a user to a team. The team you are an admin of or any team in your club, if you a club admin."""
        team = Team.get_or_none(name=team_name)
        if not team_name and (self.team_id != team.id or not self.team_admin):
            logfire.error(f"User {self.name} is not a club admin.")
            raise NotATeamAdmin("User must be a club admin to create a team.")

        if self.team_id != team.id and self.team_admin:
            logfire.error(f"User {self.name} is not a team admin for {team_name}.")
            raise NotATeamAdmin("User must be a team admin to add a user to a team.")

        team = Team.get_or_none(name=team_name)
        if team is None:
            logfire.error(f"Team {team_name} not found.")
            raise TeamNotFound("Team not found")
        user = User.get_or_none(discord_id=discord_id)
        if user is None:
            logfire.error(f"User with Discord ID {discord_id} not found.")
            raise UserNotRegistered("Discord user needs to register")
        if user.team is not None:
            logfire.error(f"User {user.name} is already in a team.")
            raise UserAlreadyOnTeam("Discord user already in a team")
        user.team_id = team.id
        user.save()
        logfire.info(f"User {user.name} added to team {team_name}.")

    @property
    def zp_url(self, markdown: bool = True):
        """Return the Zwift Power URL for the user."""
        if markdown:
            return f"[View Profile](https://zwiftpower.com/profile.php?z={self.zwid})"
        else:
            return f"https://zwiftpower.com/profile.php?z={self.zwid}"

    @property
    def zr_url(self, markdown: bool = True):
        """Return the Zwift Racing URL for the user."""
        if markdown:
            return f"[View Profile](https://www.zwiftracing.app/riders/{self.zwid})"
        else:
            return f"https://www.zwiftracing.app/riders/{self.zwid}"

    @property
    def profile(self):
        """User profile."""
        return {
            "Name": self.name,
            "zwid": self.zwid,
            "ZR Profile": self.zr_url,
            "ZP Profile": self.zp_url,
            "Discord ID": self.discord_id,
            "Discord Name": self.discord_name,
            "TOS": self.tos,
            "Active": self.active,
            "Club": self.club_id.name if self.club_id else "No Club",
            "Is Club admin": self.club_admin,
            "Team": self.team_id.name if self.team_id else "No Team",
            "Is Team admin": self.team_admin,
            "Registered": self.created_at.date().isoformat(),
            "Updated": self.updated_at.date().isoformat(),
        }

    @classmethod
    def lookup(cls, discord_id: int):
        """Lookup a user by Discord ID."""
        user = User.get_or_none(discord_id=discord_id)
        if user is None:
            logfire.error(f"User with Discord ID {discord_id} not found.")
            raise UserNotRegistered("Discord user needs to register")
        return user.profile


# Initialize the database and create the tables
def init_peewee_db():
    """Initialize the Peewee database."""
    try:
        db.connect()
        db.create_tables([User, Club, Team])
        logfire.info("Database initialized and tables created.")
        db.close()
    except OperationalError as e:
        logfire.error(f"Initialize the database: {e}", exc_info=True)
        # raise e


# if __name__ == "__main__":
#     init_peewee_db()
#
# # Example usage to create a user and associated club
# print("Creating a user and a club...")
# user = User.create(
#     name="Test User 3",
#     zwid=12345678,
#     discord_id=12345678,
#     discord_name="Test User 3",
# )
# print(user)
# club = user.create_club(club_name="Test Club 3", note="This is a test club")
# print(f"User {user.name} created club: {club.name}")

# for k, v in model_to_dict(User.get_or_none(zwid=12345678)).items():
#     print(f"{k}: {v}")
# user = User.get_or_none(zwid=12345678)
# user = User.get_or_none(User.discord_id == 12345678)
# print(user)
# user = User.lookup(12345678)
# print(user)
# team = user.create_team("Test Team 6")
# print(team)
# print(team.id == 6)

# team = Team.get_or_none(Team.discord_id == 12345678)
# print([t for t in team.admins])
