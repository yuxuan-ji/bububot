import discord
from discord.ext import commands
from .utils.Checks import is_admin, is_bot_owner
from datetime import datetime
        

class BaseCommands:
    '''Some base commands for BubuBot'''
        
    def __init__(self, client):
        self.client = client

    # Note: pass_context means that ctx contains the original context,
    #       using ctx.message gives the original Message object,
    #       using client.say() == client.send_message(ctx.message.channel,content='',*)
    
    @commands.command(pass_context=True, hidden=True)
    @commands.check(is_bot_owner)
    async def die(self, ctx):
        ''' Force disconnect the bot'''
        await self.client.say("Bubu ga shinda")
        await self.client.close()

    @commands.command(pass_context=True)
    async def test(self, ctx):
        '''Test command'''
        try:
            return await self.client.say('working!')
        except Exception as err:
            print(err)
            self.client.say('Not working')

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def changeplaying(self, ctx, *args):
        '''<gamename> *Admin'''
        statusName = " ".join(args)
        await self.client.change_presence(game=discord.Game(name=statusName))

    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        '''Prints out how long the bot has been online'''
        uptime = datetime.now() - self.client.login_time
        await self.client.say('Uptime: {}'.format(uptime))

            
def setup(client):
    client.add_cog(BaseCommands(client))