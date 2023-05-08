from Helper.__comp import *

from time import time
import discord
from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import is_dev, get_server_json

def setup(BOT):
	BOT.add_cog(Server_list(BOT))

class Server_list(cmd.Cog):
	'''
	Returns a list of all servers the bot is in currently.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['servers']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="servers")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(is_dev)
	async def slash_server_list(self, ctx):
		'''
		Returns a list of all servers the bot is in currently.
		'''

		await self.server_list(ctx)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(is_dev)
	async def server_list(self, ctx):
		out = []
		guilds = self.BRAIN.guilds
		dat = [int(x) for x in get_server_json().keys()]
		guilds.sort(key = lambda x: len(dat) - dat.index(x.id) if x.id in dat else 1000)
		for guild in guilds:
			add = ""
			try: add += f"{guild.name} - {guild.owner.name}"
			except: add += f"{guild.name}"
			try:
				invite = await guild.invites()
				add += f" - {invite[0]}"
			except: pass

			out += [add]	
		e = discord.Embed(description="\n".join(out),title="My Servers")
		await ctx.reply(embed=e)
