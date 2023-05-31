from Helper.__comp import *
from random import choice
import json, time
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user, is_dm
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Remindme(BOT))

class Remindme(cmd.Cog):
	'''
	Schedules a reminder to be sent to you in DMS after the specified duration. Format the duration as `00d00h00m` but replace `00` with the actual number of days, hours, and minutes. If you have zero of those units, you can ignore them (like `10m`).
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(duration) (content)"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="remindme")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_remindme(self, ctx, duration, content):
		'''
		Picks a random string submitted to the rst (randomly selected text) database.
		'''
		await ctx.response.defer()
		await self.remindme(ctx, duration=duration.replace(" ", ""), content=content)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def remindme(self, ctx, duration, *, content="you forgot to actually provide reminder content lmao"):
		timenow = time.time()
		with open('DB/reminders.json') as json_file:
			reminders = json.load(json_file)
		
		times = {"d":0,"h":0,"m":0}
		currStr = ""
		for x in str(duration):
			if x not in "1234567890":
				try: 
					times[x]
					times[x] = int(currStr)
				except: raise cmd.errors.ArgumentParsingError()
			else: currStr += x

		if command_user(ctx).dm_channel is None: await command_user(ctx).create_dm()

		addedTime = times['d'] * 86400 + times['h'] * 3600 + times['m'] * 60

		addReminder = [addedTime + timenow - timenow%60 - 1, str(command_user(ctx).dm_channel.id), f"Reminder from <t:{round(timenow)}:R>: {content}", command_user(ctx).id]

		reminders += [addReminder]
		open("DB/reminders.json","w").write(json.dumps(reminders,indent="\t"))

		await ctx.respond(f"Alright, reminding you in {duration}.")

		return
