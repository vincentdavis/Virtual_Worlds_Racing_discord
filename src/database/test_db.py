from db_models_mongo import ClubAdmin


def test_add_club_admin():
    """Test adding a club admin."""
    club = Club(name="Test Club", zp_club_id="12345").save()
    ClubAdmin.add_by_discord_id(club, 12345, 12345)
    assert ClubAdmin.find_by_discord_id(12345, 12345) == [club]
    club.delete()
    ClubAdmin.delete()
