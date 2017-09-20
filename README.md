Discord bot made by Chabbies


For a list of commands, use the '!b help' command


How to use:

	1) Create an app on: https://discordapp.com/developers/applications/me
	
	2) Click 'Create a Bot User'
	
	3) Grab the bot's Client ID and put it in <INSERT HERE>: https://discordapp.com/oauth2/authorize?client_id=<INSERT HERE>&scope=bot&permissions=0
	
	4) Invite the bot to your channel by clicking the above link
	
	5) Clone the repo.

	6) Install HerokuCLI and create an account, then create an app app-name.

	7) Add a database to the app.

	8) In your CLI, use heroku login, cd BubuBot, heroku git:remote -a app-name, git push heroku master.

	9) Activate the app on the app page.


VERSIONS:
	
	1.0: Basic bot with only test features.

	2.0: Added rem, megumin, clear and openpack commands. This version can be found in BubuBotUgly.

	3.0: Major overhaul: Cogs introduced for better organization, upgraded openpack to use aiohttp instead of requests, better documentation, old git repo deleted for a new one since commit history got messed up.
	
	4.0: Now hosted on Heroku. Upgraded Waifus to use a Postgresql server on heroku.