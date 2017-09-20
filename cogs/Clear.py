from discord.ext import commands
from datetime import datetime, timedelta
from .utils.Checks import is_admin


class Clear:
    '''Commands for clearing messages'''

    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def clear(self, ctx, number):
        '''<number> *Admin
        Clears a number of messages'''
        try:
            await self.client.purge_from(ctx.message.channel, limit=int(number))
        except:
            # If the maximum 14 days limit is reached, purge all until the limit
            try:
                earlierDateTime = datetime.now() - timedelta(days=14)
                await self.client.purge_from(ctx.message.channel, after=earlierDateTime)
            except Exception as err:
                await self.client.say('Unable to purge: {}'.format(err))
                print(err)


def setup(client):
    client.add_cog(Clear(client))