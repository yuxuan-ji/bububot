from discord.ext import commands
from .utils.Checks import is_admin


class Move:
    '''Commands for moving users'''

    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def move(self, ctx, userID, channelID):
        '''<userID> <channelID> *Admin
        Move an user to a specific channel'''
        try:
            user = None
            for member in self.client.get_all_members():
                if member.id == userID:
                    user = member
                    break
            channel = self.client.get_channel(id=channelID)
            await self.client.move_member(member=user, channel=channel)
        except Exception as err:
            print(err)
            self.client.say('Cannot move: {}'.format(err))

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def moveme(self, ctx, channelID):
        '''<channelID> *Admin
        Move the command author to the specified channel ID'''
        try:
            member = ctx.message.author
            channel = self.client.get_channel(id=channelID)
            await self.client.move_member(member=member, channel=channel)
        except Exception as err:
            print(err)
            await self.client.say('Cannot move: {}'.format(err))


def setup(client):
    client.add_cog(Move(client))