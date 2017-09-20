import discord
from discord.ext import commands
from datetime import datetime


# Extensions to load into BubuBot:
extensions = (
	'cogs.BaseCommands',
	'cogs.Clear',
	'cogs.Shadowverse',
	'cogs.Waifus',
	'cogs.Move',
	'cogs.Games')


class BubuBot(commands.Bot):

	import __main__
	__main__.DEBUG = False

	def __init__(self, *args, **kwargs):
		'''Initializes a BubuBot object'''
		# Bot parameters:
		super().__init__(*args, **kwargs)
		self.login_time = None  # To be updated on ready
		self.owner_id = None

		# Loading the cogs:
		for extension in extensions:
			try:
				self.load_extension(extension)
			except Exception as err:
				print('Failed to load {}'.format(extension), err)

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
			else:
				print(err)
				await self.send_message(channel, content=str(err))