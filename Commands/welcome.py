from Helper.__comp import *

from Helper.__functions import plural, is_whole, smart_lookup, is_dm, is_whole
from Helper.__action_functions import specify_server
from Helper.__server_functions import is_staff_here, modify_server, get_server_json, member_check
import discord, re, asyncio

def setup(BOT):
	BOT.add_cog(Welcome(BOT))


class Welcome(cmd.Cog):
	'''
	Manages the channel used for welcome and leave messages. By default, this is none.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(disable or channel link)`"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN



	@cmd.slash_command(name="welcome")
	@cmd.cooldown(1, 1)
	@cmd.check(is_staff_here)
	async def slash_welcome(self, ctx, args=None):
		'''
		Manages the welcome channel for the server.
		'''
		await ctx.response.defer()
		await self.welcome(ctx, arg1=args)

		return

	@cmd.check(is_staff_here)
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def welcome(self, ctx, arg1=None):
		if is_dm(ctx):
			await ctx.reply("This command cannot be used in DMs!")
			return

		if arg1 is None:
			welcome = get_server_json()[str(ctx.guild.id)][4]
			if welcome != "":
				await ctx.respond(f"The current welcome channel is <#{get_server_json()[str(ctx.guild.id)][4]}>")
			else: 
				await ctx.respond("The welcome channel is currently not configured.")
			return
		elif arg1 in ["reset", "disable", "off"]:
			modify_server(int(ctx.guild.id), welcome="")
			await ctx.respond("Welcome channel has been disabled.")
			return
		else:
			try: arg1 = str(int(re.sub("[<#> ]","",arg1)))
			except:
				await ctx.respond("Please include a valid channel to set as the welcome channel!")
				return
			
			if int(arg1) in [x.id for x in ctx.guild.text_channels]:
				modify_server(int(ctx.guild.id), welcome=arg1)
				await ctx.reply(f"Welcome channel has been set to <#{arg1}>!")
				return
			else:
				await ctx.reply("This channel does not exist in this server!")
				return


