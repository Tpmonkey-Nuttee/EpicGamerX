# discord.ext.commands.Bot custom Subclass 
# Made by Tpmonkey

import asyncio
import aiohttp
import logging
import datetime

import config

import discord
from discord.ext import commands

from db import Database

log = logging.getLogger(__name__)


class Bot(commands.Bot):
    # Subclass of commands.Bot
    def __init__(self, command_prefix, help_command=None, description=None, **options):
        # Set default Help command
        if not help_command:
            help_command = commands.DefaultHelpCommand()

        super().__init__(command_prefix, **options)

        # Define database here so It's easier to be use.
        self.database = Database()
        self.log_channel = None
        self.launch_time = datetime.datetime.now()
        self.trust_session = aiohttp.ClientSession()
        

        log.info("Bot Subclass Created.")

    @classmethod
    def create(cls) -> "Bot":
        # Create bot Instance and return

        loop = asyncio.get_event_loop()
        intents = discord.Intents().all()

        return cls(
            loop=loop,
            command_prefix=config.prefix,
            case_insensitive=False,
            max_messages=10_000,
            intents = intents
        )

    def load_extensions(self) -> None:
        # Load all extensions
        from utils.extensions import EXTENSIONS
        extensions = set(EXTENSIONS)

        for extension in extensions:
            self.load_extension(extension)

    def close(self) -> None:
        super().close()
        # os.system("kill 1")

    def add_cog(self, cog: commands.Cog) -> None:
        # just for Logging
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    async def on_message(self, message: discord.Message) -> None:
        await self.process_commands(message)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:

        if before.content != after.content:
            await self.process_commands(after)

    async def on_disconnect(self) -> None:
        pass
    
    @property
    def uptime(self):
        return datetime.datetime.now() - self.launch_time
    
    async def get_image_url(self, image: discord.Attachment) -> str:
        await image.save(open("asset/image.jpg", "wb"))
        channel = self.get_channel(config.image_channel)
        
        image = await channel.send(file=discord.File(open("asset/image.jpg", "rb")))

        image = image.attachments[0].url
  
        return image