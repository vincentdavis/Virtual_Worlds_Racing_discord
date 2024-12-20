"""Bot client implementation."""
import discord
from discord import Intents
from discord.ext import commands
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import logfire
import os

from src.utils.imports import Rider, Team, Club
from src.utils.logger import setup_logging

class VirtualWorldsBot(commands.Bot):
    """Main bot class implementing core functionality."""
    
    def __init__(self):
        # Initialize logging first
        setup_logging()
        logfire.info("Initializing Virtual Worlds Racing Bot...")
        
        # Configure bot
        intents = self._configure_intents()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            application_id=int(os.getenv("APPLICATION_ID"))
        )
        
    @staticmethod
    def _configure_intents() -> Intents:
        """Configure bot intents."""
        logfire.info("Configuring bot intents...")
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.messages = True
        return intents
        
    async def setup_hook(self) -> None:
        """Setup hook called before the bot starts."""
        logfire.info("Running setup hook...")
        await self.init_database()
        await self._load_cogs()
        
        # Sync commands with specific guild for testing
        test_guild_id = os.getenv("TEST_GUILD_ID")
        if test_guild_id:
            guild = discord.Object(id=int(test_guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            # Sync globally if no test guild specified
            await self.tree.sync()
            
        logfire.info("Setup complete!")

    async def _load_cogs(self) -> None:
        """Load all cogs."""
        cogs = ["rider", "club"]  # Start with just rider cog
        for cog in cogs:
            try:
                await self.load_extension(f"src.cogs.{cog}")
                logfire.info(f"Loaded cog: {cog}")
            except Exception as e:
                logfire.error(f"Failed to load cog {cog}: {str(e)}")

    async def init_database(self) -> None:
        """Initialize database connection."""
        try:
            logfire.info("Initializing database connection...")
            mongo_url = os.getenv("MONGO_URL")
            if not mongo_url:
                raise ValueError("MONGO_URL not set in environment")
                
            client = AsyncIOMotorClient(mongo_url)
            await init_beanie(
                database=client.VIRTUAL_WORLDS_RACING,
                document_models=[Rider, Team, Club],
            )
            logfire.info("Database initialized successfully")
        except Exception as e:
            logfire.error(f"Failed to initialize database: {str(e)}")
            raise

    async def on_ready(self):
        """Called when bot is ready."""
        logfire.info(f"Bot ready! Logged in as {self.user.name} ({self.user.id})")
        logfire.info(f"Bot is in {len(self.guilds)} servers:")
        for guild in self.guilds:
            logfire.info(f"- {guild.name} (id: {guild.id})")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """Handle any unhandled errors."""
        logfire.error(f"Unhandled error in {event_method}", exc_info=True)
        await super().on_error(event_method, *args, **kwargs)