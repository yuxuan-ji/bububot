from discord.ext import commands
import discord
import random


class Games:
	'''Contains small text-based games'''

	def __init__(self, client):
		self.client = client

	@commands.command(pass_context=True)
	async def answerme(self, ctx, *args):
		'''<question> : 100% accuracy ( ͡° ͜ʖ ͡°)'''
		if not args:
			return await self.client.say('A-Ask a question! B-Baka!!!1!!')
		
		question = " ".join(args)
		answer = random.choice(['Yes', 'No'])
		
		embed = discord.Embed()
		embed.add_field(name='Asker:', value=ctx.message.author.name)
		embed.add_field(name='Question:', value=question)
		embed.add_field(name='Answer:', value=answer)
		
		# Post the embed and delete the original command:
		await self.client.say(embed=embed)
		await self.client.delete_message(ctx.message)


def setup(client):
	client.add_cog(Games(client))
