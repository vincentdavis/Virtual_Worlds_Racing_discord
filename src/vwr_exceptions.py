class NoClubMembership(Exception):
    """Exception raised when a user does not belong to a club."""

    pass


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
    """Exception raised when a Team name not found"""

    pass


class UserAlreadyOnTeam(Exception):
    """Exception raised when a user already a member of a team."""

    pass
