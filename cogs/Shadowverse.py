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

    @commands.cooldown(10, 20)
    @sv.command(name='open', pass_context=True)
    async def sv_open(self, ctx, choice=None, *args):
        ''' <packName> (pack amount) (info)
        Sends the cards opened to the message channel.
        '''
        if not choice:
            return await postAcceptedInputs(client=self.client, choices=self.choices.keys())
        
        choice = choice.lower()

        # Parameters checking:
        INFO = False
        pack_amount = 1
        for arg in args:
            if arg.lower() == "info":
                INFO = True
            if arg.isdigit():
                pack_amount = int(arg)
        if pack_amount > 10:
            return await self.client.say("You can only open a maximum of 10 packs at a time.")
        
        try:
            packID = self.choices[choice]
            myPack = []
            
            for _ in range(pack_amount):
                myPack += PackSimulator(packID).openPack(amount=8, specialDraws=1)  # returns a list of Card objects
            
            img_urls = []
            value = ""
            
            for card in myPack:
                img_urls.append(card.img)
                # Optionally building an info embed:
                if INFO:
                    value += card.name + ', ' + card.url + '\n'

            if img_urls:
                result = await build_image(img_urls)
                result.save("roll.png")
                if not INFO:
                    await self.client.send_file(ctx.message.channel, "roll.png", content=ctx.message.author.mention)
                else:
                    await self.client.send_file(ctx.message.channel, "roll.png")
                result.close()

            # Info embed:
            if INFO:
                embed = discord.Embed()
                embed.add_field(name="Command User:", value=ctx.message.author.mention)
                embed.add_field(name="The Cards you've opened are:", value=value)
                await self.client.say(embed=embed)

            self.client.logger.debug("Opened: " + str([(card.name, card.probabilities, card.img) for card in myPack]))
        
        except KeyError:
            await self.client.say('Unidentified pack')
            await postAcceptedInputs(client=self.client, choices=self.choices.keys())


def setup(client):
    client.add_cog(Shadowverse(client))