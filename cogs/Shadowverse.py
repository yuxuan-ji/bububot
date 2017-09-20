import asyncio
import discord
from discord.ext import commands
from .PackSims.PackSimulator import PackSimulator
from .utils.Posts import postAcceptedInputs
from __main__ import DEBUG


class Shadowverse:
    '''Commands related to the Shadowverse Card Game'''
    
    def __init__(self, client):
        self.client = client
        self.choices = {
                        'standard': 'SV10001',
                        'darkness': 'SV10002',
                        'bahamut': 'SV10003',
                        'tempest': 'SV10004',
                        'wonderland': 'SV10005'
                        }

    @commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
    async def sv(self, ctx):
        '''Shadowverse extension manager'''
        subcommands = ['open']
        await postAcceptedInputs(client=self.client, choices=subcommands)

    @sv.command(name='open', pass_context=True)
    async def sv_open(self, ctx, choice=None, *args):
        ''' <packName> (show)
        Prints out the results in an Embed, and optionally the images (deleted after 10 seconds)
        '''
        if not choice:
            return await postAcceptedInputs(client=self.client, choices=self.choices.keys())
        
        # Show parameter
        SHOW = False
        if "show" in args:
            SHOW = True

        try:
            packID = self.choices[choice]
            myPack = PackSimulator(packID).openPack(amount=8, specialDraws=1)  # returns a list of Card objects
            
            imgEmbeds = []  # list containing Embed objects with the card images
            value = ""
            
            for card in myPack:
                # Building the first message:
                value += card.name + ', ' + card.url + '\n'
                # Optionally building the list of images to post:
                if SHOW:
                    embed = discord.Embed()
                    embed.set_image(url=card.img)
                    if DEBUG:
                        embed.add_field(name='DEBUG', value=card.img)
                    imgEmbeds.append(embed)

            # The first message is an Embed containing the card names and url
            embed = discord.Embed()
            embed.add_field(name="The Cards you've opened are:", value=value)
            if DEBUG:
                embed.add_field(name='DEBUG', value=[card.probabilities for card in myPack])
            firstMsg = await self.client.say(embed=embed)  # self.client.say returns a Message object

            # Then, possibly post the images to the channel and delete after x seconds
            if imgEmbeds and SHOW:
                # Posting:
                time = 5
                imgMgs = []
                for url in imgEmbeds:
                    imgMgs.append(await self.client.say(embed=url))
                    await asyncio.sleep(1)

                # Deleting:
                # Note: Tried using client.say()'s delete_after:float parameter but it wasn't as smooth as doing it manually
                imgMgs.append(await self.client.say('Deleting in {} seconds'.format(time)))
                await asyncio.sleep(time)
                try:
                    await self.client.delete_messages(imgMgs)
                except Exception as err:
                    await self.client.say('Unable to delete: {}'.format(err))
                    print(err)

            return firstMsg
        
        except KeyError:
            await self.client.say('Unidentified pack')
            await postAcceptedInputs(client=self.client, choices=self.choices.keys())
        except Exception as err:
            await self.client.say(str(err))
            await postAcceptedInputs(client=self.client, choices=self.choices.keys())


def setup(client):
    client.add_cog(Shadowverse(client))