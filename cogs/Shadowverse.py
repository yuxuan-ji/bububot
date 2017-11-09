import asyncio
import discord
from discord.ext import commands
from .PackSims.PackSimulator import PackSimulator
from .PackSims.ImageBuilder import build_image
from .utils.Posts import postAcceptedInputs


class Shadowverse:
    '''Commands related to the Shadowverse Card Game'''
    
    def __init__(self, client):
        self.client = client
        self.choices = {
                        'standard': 'SV10001',
                        'darkness': 'SV10002',
                        'bahamut': 'SV10003',
                        'tempest': 'SV10004',
                        'wonderland': 'SV10005',
                        'starforged': 'SV10006'
                        }

    @commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
    async def sv(self, ctx):
        '''Shadowverse extension manager'''
        subcommands = ['open']
        await postAcceptedInputs(client=self.client, choices=subcommands)

    @sv.command(name='open', pass_context=True)
    async def sv_open(self, ctx, choice=None, *args):
        ''' <packName> (show)
        Sends the cards opened to the message channel.
        '''
        if not choice:
            return await postAcceptedInputs(client=self.client, choices=self.choices.keys())
        
        # INFO parameter
        INFO = False
        for arg in args:
            if arg.lower() == "info":
                INFO = True

        try:
            packID = self.choices[choice]
            myPack = PackSimulator(packID).openPack(amount=8, specialDraws=1)  # returns a list of Card objects
            
            img_urls = []
            value = ""
            
            for card in myPack:
                img_urls.append(card.img)
                # Optionally building an info embed:
                if INFO:
                    value += card.name + ', ' + card.url + '\n'

            # Info embed:
            if INFO:
                embed = discord.Embed()
                embed.add_field(name="Command User:", value=ctx.message.author.mention)
                embed.add_field(name="The Cards you've opened are:", value=value)
                await self.client.say(embed=embed)

            # Then, post the images to the channel
            if img_urls:
                if not INFO:
                    await self.client.say(ctx.message.author.mention)  # Only mention if the info embed wasn't sent

                result = await build_image(img_urls)
                result.save("roll.png")
                await self.client.send_file(ctx.message.channel, "roll.png")
                result.close()

            self.client.logger.debug("Opened: " + str([(card.name, card.probabilities, card.img) for card in myPack]))
        
        except KeyError:
            await self.client.say('Unidentified pack')
            await postAcceptedInputs(client=self.client, choices=self.choices.keys())


def setup(client):
    client.add_cog(Shadowverse(client))