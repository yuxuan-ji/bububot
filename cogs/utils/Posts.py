# A module containing helpful posting functions for BubuBot and its cogs
import discord


async def postEmbedImg(client, url):
	'''Coroutine.
	Posts image of an url as an embed into the channel and returns an Embed Msg'''
	embed = discord.Embed()
	embed.set_image(url=url)
	return await client.say(embed=embed)


async def postAcceptedInputs(client, choices):
	'''Coroutine.
	Prints out the accepted inputs from a list of choices and returns an Embed Msg'''
	embed = discord.Embed()
	value = ""
	for el in choices:
		value += str(el) + '\n'
	embed.add_field(name="Accepted inputs:", value=value)
	return await client.say(embed=embed)