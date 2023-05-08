from Helper.__comp import *

import os
import sys
from time import time
from datetime import datetime

from Helper.__functions import m_line, command_user, is_dm, is_dev

def setup(BOT):
	BOT.add_cog(Restart(BOT))

class Restart(cmd.Cog):
	'''
	Forces a bot restart upon usage. The bot will report the amount of time it took to restart 
	in the channel this command was used in.
	Including the literal argument `('debug')` in the command will make the bot restart in debug 
	mode - by default, it restarts into the main Brain of TWOW Central.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`('debug')`"
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['r']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="restart")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(is_dev)
	async def slash_restart(self, ctx, debug=''):
		'''
		Forces a bot restart upon usage.
		'''

		await self.restart(ctx, debug=debug)
		return


	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(is_dev)
	async def restart(self, ctx,
		debug = ''):

		file_ref = sys.argv[0]

		debug_arg = 'debug' if debug == 'debug' else ''

		report_guild = f"1_report_guild:{'' if ctx.guild is None else ctx.guild.id}"

		report_chnl = m_line(f"""
		2_report_chnl:{command_user(ctx).id if is_dm(ctx) else ctx.channel.id}""")

		report_time = f"3_report_time:{int(time()*1000)}"

		await self.BRAIN.change_presence(status=dc.Status.invisible)
		
		await ctx.respond("♻️ **Restarting PepsiBot!**")
		print(f"Restarting on command from {command_user(ctx)} at {datetime.utcnow()}")

		os.execl(
		sys.executable, 'python', file_ref, report_guild, report_chnl, report_time, debug_arg)

		return
