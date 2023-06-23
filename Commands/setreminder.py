from Helper.__comp import *
from random import choice
import json
import time as tm
from datetime import datetime
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user, is_dm
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Setreminder(BOT))

class Setreminder(cmd.Cog):
	'''
	Schedules a reminder in the specified channel.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(duration) (content)"
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN
		


	@cmd.slash_command(name="remind")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(is_staff_here)
	async def slash_setreminder(self, ctx, time, content):
		'''
		Schedules a reminder in the channel it is used in.
		'''
		await ctx.response.defer()
		try:
			targetDt = datetime.strptime(date.today().strftime("%d/%m/%y ")+time,  "%d/%m/%y %H:%M")
		except:
			await ctx.respond("Invalid time!", ephemeral=True)

		with open('DB/reminders.json') as json_file:
			reminders = json.load(json_file)


		addReminder = [tm.mktime(targetDt.timetuple()), ctx.channel.id, f"{content}", command_user(ctx).id]

		reminders += [addReminder]
		open("DB/reminders.json","w").write(json.dumps(reminders,indent="\t"))

		await ctx.respond(f"Alright, setting reminder for {date.today().strftime('%d/%m/%y ')+time} in UTC.")

		return
