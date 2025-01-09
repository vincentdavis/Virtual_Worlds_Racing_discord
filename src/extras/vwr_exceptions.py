"""Custom Exceptions for the VWR Bot."""

# class UserNotRegistered(Exception):
#     def __init__(self, username=None, additional_message=None):
#         # Initialize with optional parameters
#         self.username = username
#         self.additional_message = additional_message
#
#     def __str__(self):
#         # Return a custom string representation of the error
#         if self.username:
#             if self.additional_message:
#                 return f"User '{self.username}' is not registered. {self.additional_message}"
#             return f"User '{self.username}' is not registered."
#         return "User is not registered."


class NoClubMembership(Exception):
    """Exception raised when a user does not belong to a club."""

    def __init__(self, discord_id: int | None = None, additional_message: str | None = None):
        # Initialize with optional parameters
        self.discord_id = discord_id
        self.additional_message = additional_message

    def __str__(self):
        # Return a custom string representation of the error
        return f"User{': '+self.discord_id if self.discord_id else ''} not a member of a club"


class NotAClubAdmin(Exception):
    """Exception raised when a user is not a club admin."""

    pass


class NotATeamAdmin(Exception):
    """Exception raised when a user is not a club admin."""

    pass


class UserNotRegistered(Exception):
    """Exception raised when a discrod user is not a registered user."""

    pass


class UserAlreadyInClub(Exception):
    """Exception raised when a user already a member of a club."""

    pass


class TeamNotFound(Exception):
    """Exception raised when a Team name, id, ....  not found"""

    pass


class ClubNotFound(Exception):
    """Exception raised when a Club  name, id, ... not found"""

    pass


class UserAlreadyOnTeam(Exception):
    """Exception raised when a user already a member of a team."""

    pass
