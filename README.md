# 🚴 Virtual Worlds Racing Discord Bot

A Discord bot designed to manage Zwift racing communities, providing registration, club management, and team organization features.


## Implemented Features

### Discord server setup:
- **Setup Roles:**
    - REGISTERED: Ths is a Role a user gets when they are registered.
    - **Automatically created roles:**
    - CLUB_<club_name>_ADMIN: This is a role for the club admin.
    - CLUB_<club_name>_MEMBER: This is a role for the club member.
    - TEAM_<club_name>_ADMIN: This is a role for the team admin.
- **Setup Categories and Channels:**
    - Channel: activity_logs, Logs most user membership activity, register, join/leave club/team.
    - Category: RIDERS, This is where all the rider channels are created.
    - Channel: Rider_help.
    - Category: CLUBS, This is where all the club channels are created.
    - Channel: club_admin, This is a channel for the club admin, create club, add admin, remove admin... create team, remove team, team admin...
    - Channel: club-<club_name>, Automatically created. This is a channel for the club, only club members can see this channel.
    - Category: TEAMS, This is where all the team channels are created.
    - Channel: team-<team_name>, Automatically created. This is a channel for the team, only team members can see this channel. All club member can access all team channels.
    - Channel: activity_logs, Logs most user membership activity, register, join/leave club/team. Can be public read
    - 
    
### User, Rider, Racer management:
- **Registration System**
- The splash command can only be used in the welcome-adn-rules channel
- **Rider Profile**
    - Secure rider registration with Zwift ID verification. (1)
    - Terms of Service and Privacy Policy acceptance
    - Duplicate registration prevention
    - Profile linking with ZwiftPower and ZwiftRacing


### Notes
1. We try to limit the data related to a Zwift_ID (zwid), until the user has participated in a race, thus verifing there zwid. 


## Plan Not implemented yet

### Rider Management
- **Registration System**
    - Secure rider registration with Zwift ID verification
    - Terms of Service and Privacy Policy acceptance
    - Duplicate registration prevention
    - Profile linking with ZwiftPower and ZwiftRacing

### Club Management
- Create and manage cycling clubs
- Link clubs with Zwift Power teams
- Manage club administrators
- Active/Inactive status tracking
- Team organization within clubs

### Team Management
- Create and organize teams within clubs
- Team administrator management
- Active status tracking

## 🛠️ Technical Stack

- **Discord API**: discord.py (pycord)
- **Database**: MongoDB with Beanie ODM
- **Logging**: Logfire
- **Configuration**: Environment variables via python-dotenv

## 📋 Prerequisites

- Python 3.8+
- MongoDB
- Discord Bot Token
- Zwift Power API access (optional)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/vincentdavis/Virtual_Worlds_Racing_discord.git
cd Virtual_Worlds_Racing_discord
```
2. Install dependencies:
```bash
uv sync --frozen
```
3. Create a `.env` file:
```bash
cp .env.example .env
```

## 🚀 Usage

### Starting the Bot

```bash
uv run main.py
```


### Available Commands

#### Rider Commands
- `/register` - Register as a new rider
- `/lookup <user>` - Look up rider information

#### Club Commands
- `/create_club <name> [zp_club_id]` - Create a new club
- `/add_team <club_name> <team_name>` - Add a team to a club
- `/remove_team <club_name> <team_name>` - Remove a team from a club
- `/add_admin <club_name> <admin_discord_id>` - Add an admin to a club
- `/remove_admin <club_name> <admin_discord_id>` - Remove an admin from a club
- `/mark_inactive <club_name>` - Mark a club as inactive
- `/mark_active <club_name>` - Mark a club as active

## 🔒 Security

- Discord ID verification
- Terms of Service acceptance required
- Duplicate registration prevention
- Admin-only actions for sensitive operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Discord.py community
- Zwift Power API
- MongoDB team
- All contributors and testers

## 📞 Support

For support, please join our [Discord server](your_discord_invite_link) or open an issue in the GitHub repository.

---
Made with ❤️ for the Zwift racing community
