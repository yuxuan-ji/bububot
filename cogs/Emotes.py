from discord.ext import commands
from .utils.Posts import postAcceptedInputs, postEmbedImg
from .utils.Checks import is_admin
import redis
import os


class Emotes:
    '''Commands to summon emotes'''

    def __init__(self, client):
        '''Client = the bot'''
        self.client = client
        self.redis_conn = None
        self.logger = self.client.logger
        # SQL table config:
        # NOTE: execute DROP TABLE locally to change columns config, will lose all data though.
        if self.client.DEBUG_MODE:
            if self.client.NO_HEROKU:
                from .utils.HerokuPostgresConn import get_conn_manual
                self.conn, self.c = get_conn_manual(self.client.DATABASE_URL)
                self.client.logger.debug("Using manual connection")
            else:
                from .utils.HerokuPostgresConn import get_conn_shell
                self.conn, self.c = get_conn_shell()
                self.client.logger.debug("Using shell connection")
        else:
            from .utils.HerokuPostgresConn import get_conn
            self.conn, self.c = get_conn()
            self.client.logger.debug("Using auto connection")
        self.c.execute("CREATE TABLE IF NOT EXISTS waifus (name TEXT, emote TEXT, url TEXT)")

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def activate_redis_cache(self, ctx, name, emote, url):
        host, port = os.environ["REDIS_URL"].split(":")
        pw = os.environ["REDIS_PW"]
        self.redis_conn = redis.StrictRedis(host=host, port=int(port), password=pw)

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def addemote(self, ctx, name, emote, url):
        '''<name> <emote> <url> *Admin
        Adds the emote to the database'''
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
    async def delemote(self, ctx, name, emote):
        '''<name> <emote> *Admin
        Deletes the emote from the database
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
    async def emote(self, ctx, *args):
        '''<name> <emote> : Summons the emote'''
        if len(args) < 2:
            # Show all available emotes:
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
            if self.redis_conn is not None:
                entry_url = self.redis_conn.hget(name, emote).decode()  # b string
                if entry_url is not None:
                    await postEmbedImg(client=self.client, url=entry_url)
            else:
                with self.conn:
                    try:
                        # Grab the url and post it using an embed:
                        self.c.execute('SELECT * FROM waifus WHERE name = %(name)s AND emote = %(emote)s',
                                       {'name': name, 'emote': emote})
                        entry = self.c.fetchone()  # returns a tuple (field1, field2, ...) or None
                        assert(isinstance(entry, tuple))
                        entry_url = entry[2]
                        await postEmbedImg(client=self.client, url=entry_url)
                        if self.redis_conn is not None:
                            self.redis_conn.hset(name, emote, entry_url)
                    except AssertionError:
                        await self.client.say("Not an entry in the database")


def setup(client):
    client.add_cog(Emotes(client))
