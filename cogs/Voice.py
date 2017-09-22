from discord.ext import commands


class Voice:
    '''Commands that require the use of a Voice Client'''

    # NOTE: use in shell: heroku buildpacks:add -i 2 https://github.com/bruchu/heroku-buildpack-ffmpeg.git
    # To add ffmpeg to heroku

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
        # Check if the input is an url or keywords:
        if (len(args) == 1) and ('youtube.com' in args[0]):  # second condition of and won't be checked if first is false, no IndexError
            url = args[0]
        else:
            keywords = args

            def _getUrl(keywords):
                # TODO: IMPLEMENT KEYWORD SEACHING
                pass

        try:
            # Join the voice channel if its not connected:
            if not self.vc_client:
                try:
                    self.vc_client = await self.client.join_voice_channel(ctx.message.author.voice_channel)
                except Exception as err:
                    print(err)
                    return
            # Play the song:
            try:
                self.player = await self.vc_client.create_ytdl_player(url)
                self.player.start()
            except Exception as err:
                print(err)
        except Exception as err:
            print(err)

    @commands.command()
    async def stop(self):
        '''Stop song, clear queue, disconnect Bot'''
        try:
            if (self.player is not None) and self.player.is_playing():
                self.player.stop()
            await self.vc_client.disconnect()
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
        except Exception as err:
            print(err)


def setup(client):
    client.add_cog(Voice(client))