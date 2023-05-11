from Helper.__comp import *

import os
import sys
from time import time
from datetime import datetime

from Helper.__functions import m_line, command_user, is_dm, is_dev, get_members

def setup(BOT):
	BOT.add_cog(Reload(BOT))

async def edit(msg, text):
	try: await msg.edit(content=text)
	except: await msg.edit_original_response(content=text)
	return

class Reload(cmd.Cog):
	'''
	Reloads several settings on the bot.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN


	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="reload")
	@cmd.cooldown(1, 1)
	@cmd.check(is_dev)
	async def slash_reload(self, ctx):
		'''
		Reloads several settings on the bot.
		'''
		await ctx.response.defer()
		await self.reload(ctx)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	@cmd.check(is_dev)
	async def reload(self, ctx):


		start = datetime.utcnow()
		text = "♻️ **Reloading PepsiBot!**"
		msg = await ctx.reply(text)


		text += "\n`Updating status...`"
		await edit(msg, text)

		await self.BRAIN.change_presence(status=dc.Status.online,
		activity=dc.Activity(type=dc.ActivityType.watching, name="{} servers with {} members".format(len(self.BRAIN.guilds), len(get_members(self.BRAIN)))))
		
		text += "\n`Reloading commands...`"
		await edit(msg, text)

		commands_loaded = []

		for cmd_name in os.listdir("Commands"):
			if not cmd_name.endswith('py') or cmd_name.startswith('__'):
				continue

			try:
				self.BRAIN.reload_extension(f"Commands.{cmd_name[:-3]}")
				commands_loaded.append(cmd_name[:-3].upper())			
			except: print(cmd_name)				
		

		text += f"\n`Reloaded the following commands: {', '.join(commands_loaded)}`"
		await edit(msg, text)

		delta = datetime.utcnow() - start
		text += f"\n✅ **Succesfully reloaded PepsiBot** in {round(delta.total_seconds(),3)} seconds."
		await edit(msg, text)

		return
