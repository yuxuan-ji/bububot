# A module containing help check functions for BubuBot and its cogs


def is_admin(ctx):
	'''Check if command user is admin'''
	user = ctx.message.author  # returns a discord.Member
	permissions = user.server_permissions
	
	# Not sure if user.server_permissions can contain more than 1 permission, so transform it to list if it's not one
	if not isinstance(permissions, list):
		permissions = [permissions]

	return any([permission.administrator for permission in permissions])


def is_bot_owner(ctx):
	'''This uses BubuBot's overloaded owner_id attribute'''
	return ctx.message.author.id == ctx.bot.owner_id