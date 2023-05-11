from Helper.__comp import *

import os
import sys
from time import time
from datetime import datetime

from Helper.__functions import m_line, command_user, is_dm, is_dev, get_members

def setup(BOT):
	BOT.add_cog(User_list(BOT))

async def edit(msg, text):
	try: await msg.edit(content=text)
	except: await msg.edit_original_response(content=text)
	return

class User_list(cmd.Cog):
	'''
	Lists all users who share a server with the bot, in alphabetical order.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['users']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN


	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="user_list")
	@cmd.cooldown(1, 1)
	@cmd.check(is_dev)
	async def slash_user_list(self, ctx):
		'''
		Lists all users who share a server with the bot, in alphabetical o
		'''
		await ctx.response.defer()
		await self.user_list(ctx)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	@cmd.check(is_dev)
	async def user_list(self, ctx):

		member_list = sorted([x.name+"#"+x.discriminator for x in get_members(self.BRAIN)])
		open("user_list.txt","w",encoding="utf-8").write("\n".join(member_list))
		await ctx.reply(f"Here's a list of all **{len(member_list)}** users.",file=dc.File("user_list.txt"))
		os.remove("user_list.txt")

		return
