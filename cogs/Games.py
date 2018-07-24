from discord.ext import commands
import discord
import random
import aiohttp


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
        embed.add_field(name='Asker:', value=ctx.message.author.mention)
        embed.add_field(name='Question:', value=question)
        embed.add_field(name='Answer:', value=answer)
        
        # Post the embed and delete the original command:
        await self.client.say(embed=embed)
        await self.client.delete_message(ctx.message)

    @commands.cooldown(1, 15)
    @commands.command(pass_context=True)
    async def predict(self, ctx, url):
        '''<jpg url> : This better be a jpg or I will slap you'''
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url) as resp:
                    image_data = await resp.read()
                    return await self.client.say(self.client.SakuModel.predict(image_data))

        except Exception as e:
            return await self.client.say('bruh...')


def setup(client):
    client.add_cog(Games(client))
