from discord.ext import commands
from .utils.opus_loader import load_opus_lib
from datetime import timedelta
import time
import asyncio
# Heroku doesn't have ffmpeg and libopus, so run the following in shell:
# heroku buildpacks: add -i 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest
# heroku buildpacks:add -i 3 https://github.com/heroku/heroku-buildpack-apt


class Voice:
    '''Commands that require the use of a Voice Client'''

    def __init__(self, client):
        self.client = client
        self.vc_client = None
        self.player = None
        self.player_volume = 0.10

    def _cleanup(self):
        '''Resets the attributes to default'''
        self.vc_client = None
        self.player = None

    async def disconnect_timer(self):
        '''Disconnect after a minute of inactivity'''
        stop_time = None
        while self == self.client.get_cog('Voice'):
            if (self.vc_client is not None) and (self.player is not None):
                # Whenever a song is playing, overwrite stop_time:
                if self.player.is_playing():
                    stop_time = None

                # When a song has stopped playing, register stop_time and disconnect after a minute:
                if self.player.is_done():
                    if stop_time:
                        if int((time.time() - stop_time)) > 60:
                            await self.vc_client.disconnect()
                            self._cleanup()
                            stop_time = None
                        continue  # skip the below if stop_time is registered, we don't want to overwrite it
                    stop_time = time.time()
                
            await asyncio.sleep(5)

    @commands.command(pass_context=True)
    async def play(self, ctx, *args):
        '''<url|keywords>'''
        if (self.player is not None) and self.player.is_playing():
            return await self.client.say("Wait for current song to finish, my lazy ass didn't implement queues")
        if not args:
            return await self.client.say('G-Gimme something to play! B-Baka!!!1!!')
        
        url = " ".join(args)

        # Join the voice channel if its not connected:
        if not self.vc_client:
            try:
                self.vc_client = await self.client.join_voice_channel(ctx.message.author.voice_channel)
            except Exception as err:
                await self.client.say('Could not join the voice channel')
                self._cleanup()
                print(err)
        
        # Play the song, with auto searching for keywords enabled:
        try:
            opts = {'default_search': 'auto',
                    'quiet': True}
            self.player = await self.vc_client.create_ytdl_player(url, ytdl_options=opts)
            self.player.volume = self.player_volume
            self.player.start()
            
            title = self.player.title
            uploader = self.player.uploader
            duration = str(timedelta(seconds=int(self.player.duration)))
            views = self.player.views
            # **word** is bold in discord:
            await self.client.say("Playing **{}** by **{}** :  [{}]  [{} views]".format(title, uploader, duration, views))
        
        except Exception as err:
            await self.client.say('Could not create a player')
            self._cleanup()
            print(err)

    @commands.command()
    async def stop(self):
        '''Stop song, clear queue, disconnect Bot'''
        if (self.player is not None) and (self.player.is_playing()):
            self.player.stop()
        if self.vc_client is not None:
            await self.vc_client.disconnect()
        else:
            await self.client.say("Not connected")
        self._cleanup()

    @commands.command()
    async def skip(self):
        '''Skip song'''
        if (self.player is not None) and self.player.is_playing():
            self.player.stop()
            self.player = None
        else:
            await self.client.say("No song playing")


def setup(client):
    load_opus_lib()
    n = Voice(client)
    client.add_cog(n)
    client.loop.create_task(n.disconnect_timer())