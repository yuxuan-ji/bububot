from discord.ext import commands
from .utils.opus_loader import load_opus_lib
# Heroku doesn't have ffmpeg and libopus, so run the following in shell:
# heroku buildpacks: add -i 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest
# heroku buildpacks:add -i 3 https://github.com/heroku/heroku-buildpack-apt


class Voice:
    '''Commands that require the use of a Voice Client'''

    def __init__(self, client):
        self.client = client
        self.vc_client = None
        self.player = None

    def _cleanup(self):
        '''Resets the attributes to default'''
        self.vc_client = None
        self.player = None

    @commands.command(pass_context=True)
    async def play(self, ctx, *args):
        '''<url|keywords>'''
        if (self.player is not None) and self.player.is_playing():
            return await self.client.say("Wait for current song to finish, my lazy ass didn't implement queues")
        if not args:
            return await self.client.say('G-Gimme something to play! B-Baka!!!1!!')
        
        url = " ".join(args)

        try:
            # Join the voice channel if its not connected:
            if not self.vc_client:
                try:
                    self.vc_client = await self.client.join_voice_channel(ctx.message.author.voice_channel)
                except Exception as err:
                    print(err)
                    return
            # Play the song, with auto searching for keywords enabled:
            try:
                opts = {'default_search': 'auto',
                        'quiet': True}
                self.player = await self.vc_client.create_ytdl_player(url, ytdl_options=opts)
                self.player.start()
            except Exception as err:
                print(err)
        except Exception as err:
            print(err)

    @commands.command()
    async def stop(self):
        '''Stop song, clear queue, disconnect Bot'''
        try:
            if (self.player is not None) and (self.player.is_playing()):
                self.player.stop()
            if self.vc_client is not None:
                await self.vc_client.disconnect()
            else:
                await self.client.say("Not connected")
        except Exception as err:
            print(err)
        finally:
            self._cleanup()

    @commands.command()
    async def skip(self):
        '''Skip song'''
        try:
            if (self.player is not None) and self.player.is_playing():
                self.player.stop()
            else:
                await self.client.say("No song playing")
        except Exception as err:
            print(err)


def setup(client):
    load_opus_lib()
    client.add_cog(Voice(client))