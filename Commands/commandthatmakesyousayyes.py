from Helper.__comp import *
from random import randint
from time import time
import discord as dc
from copy import deepcopy
from Helper.__config import STARTUP
from Helper.__functions import m_line, is_slash_cmd, command_user
from Helper.__server_functions import member_check


def setup(BOT):
	BOT.add_cog(Commandthatmakesyousayyes(BOT))

class Commandthatmakesyousayyes(cmd.Cog):
	'''
	Command that sends a webhook message that's your profile saying the word "yes"
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['yes']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="ctmysy")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_commandthatmakesyousayyes(self, ctx):
		'''
		Command that sends a webhook message that's your profile saying the word "yes"
		'''
		await ctx.response.defer()
		await self.commandthatmakesyousayyes(ctx)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def commandthatmakesyousayyes(self, ctx):
		token = open("DB/token.txt",'r').read()
		
		channel = ctx.channel
		found_hook = False
		for x in await channel.webhooks():
			if x.user == self.BRAIN.user:
				myWebhook = x
				found_hook = True

		if not found_hook:
			myWebhook = await channel.create_webhook(name=f"PepsiHook @ {channel.name}", avatar=await self.BRAIN.user.avatar.read())
			
		me = command_user(ctx)
		await myWebhook.send(content="yes", username=me.display_name, avatar_url=me.display_avatar.url)
		if is_slash_cmd(ctx): await ctx.respond("** **",ephemeral=True,delete_after=0)
		return
