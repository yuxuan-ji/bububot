import discord
from discord.ext import commands
from datetime import datetime
import logging

# Extensions to load into BubuBot:
BASE_EXTENSIONS = (
    'cogs.BaseCommands',
    'cogs.Clear',
    'cogs.Shadowverse',
    'cogs.Waifus',
    'cogs.Move',
    'cogs.Voice',
    'cogs.Games')


class BubuBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        '''Initializes a BubuBot object'''
        # Bot parameters:
        self.login_time = None  # To be updated on ready
        self.owner_id = None
        self.DEBUG_MODE = kwargs.pop('DEBUG_MODE', False)
        self.DATABASE_URL = kwargs.pop('DATABASE_URL', None)
        self.NO_HEROKU = kwargs.pop('NO_HEROKU', False)
        extensions = kwargs.pop('extensions', BASE_EXTENSIONS)
        self.logger = self.set_logger(self.DEBUG_MODE)

        super().__init__(*args, **kwargs)
        
        # Loading the cogs:
        for extension in extensions:
            try:
                self.load_extension(extension)
            except Exception as err:
                self.logger.exception('Failed to load {}'.format(extension))

        # Base events:
        @self.event
        async def on_ready():
            # Grabbing the bot's app info:
            # *this needs to be saved in a variable or you can't access its content
            app_info = await self.application_info()  # returns a namedtuple
            
            # Setting up some bot attributes:
            self.owner_id = app_info.owner.id
            self.login_time = datetime.now()
            await self.change_presence(game=discord.Game(name='waga na wa bubu'))

            # Login log messages:
            print('Logged in as')
            print(self.user.name)
            print(self.user.id)
            print('OwnerID: {}'.format(self.owner_id))
            print('------')

        @self.event
        async def on_command_error(err, ctx):
            channel = ctx.message.channel
            if isinstance(err, commands.CheckFailure):
                await self.send_message(channel, content="Insufficient permissions")
            elif isinstance(err, commands.CommandNotFound):
                await self.send_message(channel, content="Not a command")
            elif isinstance(err, commands.CommandOnCooldown):
                await self.send_message(channel, content="{} Chillax my dude".format(ctx.message.author.mention))
            else:
                self.logger.exception("Unexpected error: {}--{}--{}".format(err, ctx.message.content, channel))
                await self.send_message(channel, content="Something bad happened")

    @staticmethod
    def set_logger(DEBUG_MODE=False):
        """Create a logger on debug mode or info mode"""
        if DEBUG_MODE:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logger = logging.getLogger(__name__)
        logger.setLevel(level)

        bot_format = logging.Formatter(
            '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
            '%(message)s',
            datefmt="[%d/%m/%Y %H:%M]")

        # Create a handler that prints to stdout:
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(bot_format)
        stdout_handler.setLevel(level)

        logger.addHandler(stdout_handler)

        return logger
