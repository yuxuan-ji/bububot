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
                        'starforged': 'SV10006',
                        'chrono': 'SV10007',
                        }

    @commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
    async def sv(self, ctx):
        '''Shadowverse extension manager'''
        subcommands = ['open']
        await postAcceptedInputs(client=self.client, choices=subcommands)

    @commands.cooldown(10, 20)
    @sv.command(name='open', pass_context=True)
    async def sv_open(self, ctx, choice=None, pack_amount='1'):
        ''' <packName> (pack amount)
        Sends the cards opened to the message channel.
        '''
        if not choice:
            return await postAcceptedInputs(client=self.client, choices=self.choices.keys())
        choice = choice.lower()
        try:
            pack_amount = int(pack_amount)
        except:
            return await self.client.say("Invalid amount")
        if pack_amount > 10:
            return await self.client.say("You can only open a maximum of 10 packs at a time.")
        if pack_amount <= 0:
            return
            
        try:
            packID = self.choices[choice]
            myPack = []
            
            for _ in range(pack_amount):
                myPack += PackSimulator(packID).openPack(amount=8, specialDraws=1)  # returns a list of Card objects
            
            img_urls = []
            
            for card in myPack:
                img_urls.append(card.img)

            result = await build_image(img_urls)
            result.save("roll.png")
            await self.client.send_file(ctx.message.channel, "roll.png", content=ctx.message.author.mention)
            result.close()  # Result is a PIL image that must be closed

            self.client.logger.debug("Opened: " + str([(card.name, card.probabilities, card.img) for card in myPack]))
        
        except KeyError:
            await self.client.say('Unidentified pack')
            await postAcceptedInputs(client=self.client, choices=self.choices.keys())


def setup(client):
    client.add_cog(Shadowverse(client))