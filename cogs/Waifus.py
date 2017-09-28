from discord.ext import commands
from .utils.Posts import postAcceptedInputs, postEmbedImg
from .utils.Checks import is_admin


class Waifus:
    '''Commands to summon waifus'''

    def __init__(self, client):
        '''Client = the bot'''
        self.client = client
        # SQL table config:
        # NOTE: execute DROP TABLE locally to change columns config, will lose all data though.
        if self.client.DEBUG_MODE:
            from .utils.HerokuPostgresConn import get_manual_conn
            self.conn, self.c = get_manual_conn()
            self.client.logger.debug("Using manual connection")
        else:
            from .utils.HerokuPostgresConn import get_conn
            self.conn, self.c = get_conn()
            self.client.logger.debug("Using auto connection")
        self.c.execute("CREATE TABLE IF NOT EXISTS waifus (name TEXT, emote TEXT, url TEXT)")

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def addwaifu(self, ctx, name, emote, url):
        '''<name> <emote> <url> *Admin
        Adds the waifu to the database'''
        try:
            with self.conn:
                # Check if the entry already exists:
                self.c.execute('SELECT * FROM waifus WHERE name = %(name)s AND emote = %(emote)s',
                               {'name': name, 'emote': emote})
                if self.c.fetchone():
                    await self.client.say('That already exists')
                # Else, we insert it into the table
                else:
                    self.c.execute("INSERT INTO waifus VALUES (%(name)s, %(emote)s, %(url)s)",
                                   {'name': name, 'emote': emote, 'url': url})
                    await self.client.say('Added {} {}'.format(name, emote))
                    self.client.logger.info("Entry {} {} was added to the database".format(name, emote))
        except Exception as err:
            await self.client.say("Could not add to the database")
            self.client.logger.exception("Could not add to the database")

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def delwaifu(self, ctx, name, emote):
        '''<name> <emote> *Admin
        Deletes the waifu from the database
        '''
        try:
            with self.conn:
                self.c.execute('DELETE FROM waifus WHERE name = %(name)s AND emote = %(emote)s',
                               {'name': name, 'emote': emote})
                await self.client.say('Deleted {} {}'.format(name, emote))
                self.client.logger.info('Deleted {} {} from the database'.format(name, emote))
        except Exception as err:
            await self.client.say("Could not delete from the database")
            self.client.logger.exception("Could delete from the database")

    @commands.command(pass_context=True)
    async def waifu(self, ctx, *args):
        '''<name> <emote> : Summons the waifu'''
        if len(args) < 2:
            # Show all available waifus and emotes:
            with self.conn:
                try:
                    self.c.execute('SELECT * FROM waifus')
                    entries = self.c.fetchall()  # returns a list of tuples (field1, field2, ...) or None
                    assert(isinstance(entries, list))
                    # Remove the urls
                    entries_no_url = sorted([' '.join([rows[0], rows[1]]) for rows in entries])
                    await postAcceptedInputs(client=self.client, choices=entries_no_url)
                except AssertionError:
                    await self.client.say('No waifus added yet')
        else:
            name = args[0]
            emote = args[1]
            with self.conn:
                try:
                    # Grab the url and post it using an embed:
                    self.c.execute('SELECT * FROM waifus WHERE name = %(name)s AND emote = %(emote)s',
                                   {'name': name, 'emote': emote})
                    entry = self.c.fetchone()  # returns a tuple (field1, field2, ...) or None
                    assert(isinstance(entry, tuple))
                    entry_url = entry[2]
                    await postEmbedImg(client=self.client, url=entry_url)
                except AssertionError:
                    await self.client.say("Not an entry in the database")


def setup(client):
    client.add_cog(Waifus(client))
