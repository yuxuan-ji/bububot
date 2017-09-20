from BubuBot import BubuBot
import os

if __name__ == '__main__':
    import __main__
    __main__.DEBUG = False
    BOT_TOKEN = os.environ["DISCORD_TOKEN"]  # You must first use heroku config:set DISCORD_TOKEN=YOURBOTTOKEN in your shell
    # BOT_TOKEN = "INSERT YOUR BOT TOKEN"  # If you're not using heroku, directly insert your token here and delete the above line
    BubuBot(command_prefix='!b ').run(BOT_TOKEN)