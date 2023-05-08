from Helper.__comp import *

from Helper.__functions import plural, is_whole, smart_lookup, is_dm, is_whole
from Helper.__action_functions import specify_server
from Helper.__server_functions import is_staff
import discord, cexprtk, asyncio, eventlet, time
import func_timeout as ft

def setup(BOT):
	BOT.add_cog(Spoiler(BOT))

class Spoiler(cmd.Cog):
	'''
	Generates a 49 message spoiler wall with a closing message. 
    Spoiler walls can be formatted using curly braces `{}` containing some expression, and you can include the variable 'x' as a sub-in for the current message number, starting from 1. For example, {50-x} will count down from 49 to 1.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(*spoiler)`"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['spoilerwall']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="spoiler")
	@cmd.cooldown(1, 15, cmd.BucketType.user)
	@cmd.check(is_staff)
	async def slash_spoiler(self, ctx, template = ''):
		'''
		Generates a 49 message spoiler wall with a closing message. 
		'''

		await self.spoiler(ctx, template)

		return


	@cmd.check(is_staff)
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 15, cmd.BucketType.user)
	async def spoiler(self, ctx,
		*, spoiler=""):
		template = spoiler
		if template.strip() == "":
			template = "{x}"

		substrings = []
		in_brackets = False
		escaped = False
		current_substring = ""
		cleaned_temp = ""
		num = 0
		for c in template:
			if c == "{" and not in_brackets and not escaped:
				in_brackets = True
				cleaned_temp += c + f'0[{num}]'
			elif c == "}" and in_brackets and not escaped:
				substrings.append(current_substring)
				num += 1
				current_substring = ""
				in_brackets = False
				cleaned_temp += c
			elif in_brackets:
				if c != "\\" or escaped:
				    current_substring += c
				else:
					cleaned_temp += c
			else:
				cleaned_temp += c
			escaped = c == "\\"

		if current_substring:
			substrings.append(current_substring)
		e = {}
		st = cexprtk.Symbol_Table({'x':0},add_constants=True)
		for fx in range(49):
			st.variables['x'] = fx+1
			e = {}
			for x in range(len(substrings)):
				test = cexprtk.Expression(substrings[x].replace("while","wile"),st)
				try:
					e[x] = test.value()
				except Exception as error:
					await ctx.channel.send("Your input could not be parsed!")
					return
				if is_whole(e[x]): e[x] = int(e[x])
			await ctx.channel.send(cleaned_temp.format(e))
		await ctx.channel.send("```\nSpoiler wall closed.```")
		return
