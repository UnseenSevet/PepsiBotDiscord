from Helper.__comp import *
from random import choice
import json, pytz, re
import time as tm
from time import time
from dateutil import parser
from functools import partial
from datetime import datetime, date
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user, is_dev, get_channel, safe_cut, is_dm
from Helper.__server_functions import member_check, is_staff_here
from Helper.__bpp_functions import safe_cut

def setup(BOT):
	BOT.add_cog(Reminder(BOT))

class Reminder(cmd.Cog):
	'''
	A group of commands to set and manage reminders, generally for TWOW.

	With `/reminder self [duration] [content]`, you can schedule reminders to be DMed to you once the duration is elapsed. Schedules a reminder to be sent to you in DMS after the specified duration. Format the duration as `00d00h00m` but replace `00` with the actual number of days, hours, and minutes. If you have zero of those units, you can ignore them (like `10m`).

	With `/reminder add [time] [content]`, you can set a reminder to be at any point in the future, and the command will parse most common date/time formats. Once the time you input arrives, the message content will be sent in the channel you sent it in, or the channel you specify if you specify a channel. When you're using this as a text command, you must put quotes around the time argument or the command will not parse it correctly.

	With `/reminder group [time] [template]`, can also schedule up to eight reminders leading up to a certain time. (2d > 1d > 12h > 6h > 3h > 2h > 1h > 30m). `{time}` will be substituted with the time remaining until the scheduled time in each reminder when put in the template argument. When you're using this as a text command, you must put quotes around the time argument or the command will not parse it correctly.

	With `/reminder manage`, a menu to manage your active reminders will be created. 

	With `/reminder timezone [timezone]`, you can update your timezone to be whatever you want for the purposes of parsing time.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(*args)"
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['remindme','remind']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN
		
	reminder = dc.SlashCommandGroup("reminder", "Commands for managing reminders")

	@cmd.command(name="remindme")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def remindme(self, ctx, duration, *, content):
		'''
		Schedules a reminder to be sent to you in DMS after the specified duration.
		'''
		await self.reminder_me(ctx, duration=duration.replace(" ", ""), content=content)

		return

	@reminder.command(name="self")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def reminder_me(self, ctx, duration, content="you forgot to actually provide reminder content lmao"):
		timenow = time()
		with open('DB/reminders.json') as json_file:
			reminders = json.load(json_file)

		if len([x for x in reminders if x['owner'] == command_user(ctx).id]) >= 40: 
			await ctx.respond("You cannot have more than 40 pending reminders at once!", ephemeral=True)
		
		times = {"d":0,"h":0,"m":0}
		currStr = ""
		for x in str(duration):
			if x not in "1234567890":
				try: 
					times[x]
					times[x] = int(currStr)
				except: raise cmd.errors.ArgumentParsingError()
			else: currStr += x

		channel = command_user(ctx).dm_channel
		if channel is None: channel = await command_user(ctx).create_dm()

		addedTime = times['d'] * 86400 + times['h'] * 3600 + times['m'] * 60

		addReminder = {'time':addedTime + timenow - timenow%60 - 1, 'channel': str(channel.id), 'content':content, 'owner':command_user(ctx).id, 'type':f'personal {int(timenow)}'}

		reminders += [addReminder]
		open("DB/reminders.json","w").write(json.dumps(reminders,indent="\t"))

		await ctx.respond(f"Alright, reminding you in {duration}.", ephemeral=True)

		return

	@reminder.command(name="add")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(is_staff_here)
	async def slash_reminder_add(self, ctx, time, content, channel=None):
		'''
		Schedules a reminder in the channel it is used in.
		'''

		with open('DB/reminders.json') as json_file:
			reminders = json.load(json_file)

		if len([x for x in reminders if x['owner'] == command_user(ctx).id]) >= 40: 
			await ctx.respond("You cannot have more than 40 pending reminders at once!")
			return

		with open('DB/timezones.json') as json_file:
			timezones = json.load(json_file)

		if str(command_user(ctx).id) not in timezones.keys():
			await ctx.respond("You have not given your timezone to me yet! Do so with /remind timezone.",ephemeral=True)
			return

		tz = pytz.timezone(timezones[str(command_user(ctx).id)])
		

		if channel != None:
			try: channel = int(re.sub("[<#> ]","",channel))
			except:
				await ctx.respond("Please include a valid channel to remind in!",ephemeral=True)
				return
			if channel in [x.id for x in ctx.guild.text_channels]:
				channel = [x for x in ctx.guild.text_channels if x.id == channel][0]
		else:
			channel = ctx.channel


		if channel.type == dc.ChannelType.private:
			await ctx.respond("You can't set reminders in DM channels! Try /remindme instead.",ephemeral=True)
			return

		strtimezone = timezones[str(command_user(ctx).id)]

		try:

			targetDT = datetime.now(tz)
			targetDT = parser.parse(f"{time}",ignoretz=True)
			try: targetDT = tz.localize(targetDT)
			except:	targetDT = tz.localize(targetDT,is_dst=False)


		except Exception as e:
			raise e
			await ctx.respond("Invalid time!", ephemeral=True)
			return


		timenow = tm.time()
		newtime = tm.mktime(targetDT.astimezone(pytz.timezone("US/Central")).timetuple())
		
		while newtime < timenow: newtime += 86400

		targetDT = datetime.fromtimestamp(newtime).astimezone(tz)
		content = content.replace('\\n','\n')
		addReminder = {'time':newtime-1, 'channel':ctx.channel.id, 'content':content, 'owner':command_user(ctx).id,'type':'all'}

		reminders += [addReminder]
		open("DB/reminders.json","w").write(json.dumps(reminders,indent="\t"))

		await ctx.respond(f"Alright, setting reminder for {targetDT.strftime('%b %d, %Y %I:%M %p in %Z')}",ephemeral=True)

		return


	@reminder.command(name="group")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(is_staff_here)
	async def slash_reminder_group(self, ctx, time, template, channel=None):
		'''
		Schedules a reminder group. Use {time} to substitue for time remaining in the template argument.
		'''

		content = template

		with open('DB/reminders.json') as json_file:
			reminders = json.load(json_file)

		with open('DB/timezones.json') as json_file:
			timezones = json.load(json_file)

		if str(command_user(ctx).id) not in timezones.keys():
			await ctx.respond("You have not given your timezone to me yet! Do so with /remind timezone.",ephemeral=True)
			return

		tz = pytz.timezone(timezones[str(command_user(ctx).id)])
		

		if channel != None:
			try: channel = int(re.sub("[<#> ]","",channel))
			except:
				await ctx.respond("Please include a valid channel to remind in!",ephemeral=True)
				return
			if channel in [x.id for x in ctx.guild.text_channels]:
				channel = [x for x in ctx.guild.text_channels if x.id == channel][0]
		else:
			channel = ctx.channel


		if channel.type == dc.ChannelType.private:
			await ctx.respond("You can't set reminders in DM channels! Try /remindme instead.",ephemeral=True)
			return

		strtimezone = timezones[str(command_user(ctx).id)]

		try:

			targetDT = datetime.now(tz)
			targetDT = parser.parse(f"{time}",ignoretz=True)
			try: targetDT = tz.localize(targetDT)
			except:	targetDT = tz.localize(targetDT,is_dst=False)


		except Exception as e:
			raise e
			await ctx.respond("Invalid time!", ephemeral=True)
			return


		timenow = tm.time()
		newtime = tm.mktime(targetDT.astimezone(pytz.timezone("US/Central")).timetuple())
		
		while newtime < timenow: newtime += 86400

		targetDT = datetime.fromtimestamp(newtime).astimezone(tz)
		content = content.replace('\\n','\n')
		addReminder = {'time':newtime-1, 'channel':ctx.channel.id, 'content':content, 'owner':command_user(ctx).id,'type':'all'}
		
		myReminds = len([x for x in reminders if x['owner'] == command_user(ctx).id])
		adds = [86400*2,86400,43200,21600,10800,7200,3600,1800]
		times = ['2 days', '1 day', '12 hours', '6 hours', '3 hours', '2 hours', '1 hour', '30 minutes']
		for x in range(len(adds)):
			
			newAdd = addReminder.copy()
			newAdd['time'] -= adds[x]
			newAdd['content'] = newAdd['content'].replace("{time}", times[x])

			if newAdd['time'] > timenow:
				reminders += [newAdd.copy()]
				myReminds += 1

			if myReminds > 40: 
				await ctx.respond("You cannot have more than 40 pending reminders at once!")
				return

		open("DB/reminders.json","w").write(json.dumps(reminders,indent="\t"))

		await ctx.respond(f"Alright, setting reminders leading up until {targetDT.strftime('%b %d, %Y %I:%M %p in %Z')}",ephemeral=True)

		return



	@reminder.command(name="manage")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_reminder_list(self, ctx):
		'''
		Helps you manage all your active reminders.
		'''
		await ctx.response.defer()

		prev_rem = Button(
			label = "Up", emoji = "⬆️", style = dc.ButtonStyle.blurple,
			disabled = True, custom_id = f"{command_user(ctx).id} {int(time() * 1000)} p0"
		)

		next_rem = Button(
			label = "Down", emoji = "⬇️", style = dc.ButtonStyle.blurple, 
			custom_id = f"{command_user(ctx).id} {int(time() * 1000)} p2"
		)

		delete_rem = Button(
			label = "Remove", emoji = "❌", row=1, style = dc.ButtonStyle.blurple, 
			custom_id = f"{command_user(ctx).id} {int(time() * 1000)} px"
		)

		prev_rem.callback = self.manager_embed
		next_rem.callback = self.manager_embed
		delete_rem.callback = self.manager_embed

		full_view = View()

		full_view.add_item(prev_rem)
		full_view.add_item(next_rem)
		full_view.add_item(delete_rem)

		out_embed, full_view, display_view = await self.manager_embed(cmd_user=command_user(ctx), full_view=full_view)

		msg = await ctx.respond(embed=out_embed, view=display_view)
		print(type(msg))
		cb_help = partial(self.manager_embed, full_view = full_view)
		prev_rem.callback = cb_help
		next_rem.callback = cb_help
		delete_rem.callback = cb_help

		await display_view.wait()
		
		await msg.edit(view=None)


	async def manager_embed(self, ctx=None, term=None, cmd_user=None, full_view=None):
		page_n = 1
		page_total = 1
		embed = None

		if not ctx is None: # If this is an Interaction, find the search term + interaction data

			await ctx.response.defer()
			c_id_args = ctx.data['custom_id'].split(" ")

			cmd_user_id = int(c_id_args[0])

			if ctx.user.id != cmd_user_id: # Only the command user can use the view
				return

			cmd_user = dc.utils.get(self.BRAIN.users, id=cmd_user_id)
		
			if c_id_args[2][1:] == 'x':
				page_n == 1
				out = ctx.message.embeds[0].description.strip().split("\n\n")
				for xn in range(len(out)):
					if out[xn].startswith("**->**"):
						page_n = int(out[xn][7:].split("\\.")[0])

				with open('DB/reminders.json') as json_file:
					reminders = json.load(json_file)

				myReminders = [x for x in reminders if x['owner'] == cmd_user_id]
				myReminders.sort(key=lambda x: int(x['time']))

				removed = myReminders[page_n-1]
				reminders.remove(removed)
				myReminders.remove(removed)

				if page_n > len(myReminders): page_n = len(myReminders)
				
				out = ""
				for xn in range(max(page_n-8,0),min(len(myReminders),max(page_n,8))):
					x = myReminders[xn]
					content = safe_cut(x['content'],30).replace('\n','\\n')
					out += f"{'**->** ' if xn+1 == page_n else ''}{xn+1}\\. {'In DMs' if 'personal' in x['type'] else 'In <#'+str(x['channel'])+'>'} at <t:{int(x['time'])+1}>: `{content}`\n\n"

				embed = dc.Embed(title=f'Your Reminders (Selected #{page_n})',description=out.strip())		
				content = safe_cut(removed['content'],20).replace('\n','\\n')
				embed.set_footer(text=f"Removed reminder {'In DMs' if 'personal' in removed['type'] else 'In <#'+str(removed['channel'])+'>'} at <t:{int(removed['time'])+1}>: `{content}")
			
				open("DB/reminders.json","w").write(json.dumps(reminders,indent="\t"))
				page_total = len(myReminders)
			
			else: page_n = int(c_id_args[2][1:])

		try: embeds = ctx.message.embeds
		except: embeds = []



		if embed is None:
			with open('DB/reminders.json') as json_file:
				reminders = json.load(json_file)

			myReminders = [x for x in reminders if x['owner'] == cmd_user.id]
			myReminders.sort(key=lambda x: int(x['time']))

			out = ""

			for xn in range(max(page_n-8,0),max(page_n,8)):
				x = myReminders[xn]
				content = safe_cut(re.sub("<@&\d{1,20}>", "@role", x['content']),30).replace('\n','\\n')
				out += f"{'**->** ' if xn+1 == page_n else ''}{xn+1}\\. {'In DMs' if 'personal' in x['type'] else 'In <#'+str(x['channel'])+'>'} at <t:{int(x['time'])+1}>: `{content}`\n\n"
			page_total = len(myReminders)

			embed = dc.Embed(title=f'Your Reminders (Selected #{page_n})',description=out.strip())

			
		new_items = []

		for c in full_view.children:
			c_id_args = c.custom_id.split(" ")
			
			if type(c).__name__ == "Button":

				if c.emoji.name == "⬆️":
					c_id_args[-1] = f"p{page_n-1}"

					if page_n == 1:
						c.disabled = True
					else:
						c.disabled = False
				
				if c.emoji.name == "⬇️":
					c_id_args[-1] = f"p{page_n+1}"

					if page_n >= page_total:
						c.disabled = True
					else:
						c.disabled = False


			c.custom_id = " ".join(c_id_args)

			new_items.append(c)

		# Separate a display_view from the comprehensive full_view to exclude unnecessary buttons
		display_view = View()
		full_view.clear_items()

		for c in new_items:
			full_view.add_item(c)

			if type(c).__name__ != "Button" or page_total > 1 or (c.emoji.name == "❌" and page_total > 0):
				display_view.add_item(c)

		if ctx is None:
			return [embed, full_view, display_view]
		else:
			await ctx.edit_original_response(embed=embed, view=display_view)
			return


	async def tzAutocomplete(ctx):
		return [x for x in pytz.common_timezones if ctx.value.lower() in x.lower()]

	@reminder.command(name='timezone')
	@cmd.cooldown(1,3,cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_reminder_tz(self,ctx,timezone: dc.Option(input_type=str,autocomplete=tzAutocomplete)):
		try:
			tz = pytz.timezone(timezone)
		except:
			await ctx.respond("This is not a valid timezone! Please enter a timezone name that comes up in the autocomplete.",ephemeral=True)
			return

		with open('DB/timezones.json') as json_file:
			timezones = json.load(json_file)
		timezones[str(command_user(ctx).id)] = timezone

		open("DB/timezones.json","w").write(json.dumps(timezones,indent="\t"))
		await ctx.respond(f"Updated your timezone to {timezone}!",ephemeral=True)
		
