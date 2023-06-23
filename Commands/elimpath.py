from Helper.__comp import *
from random import randint, choice
from time import time
import discord as dc
import re
from copy import deepcopy
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user
from Helper.__server_functions import member_check
from math import *

def better_round(n):
	if n % 1 >= 0.5: return ceil(n)
	else: return floor(n)

def parse_str(n, x):
	try:
		float(n[:-1] if n[-1] == "%" else n)
	except:
		return None

	if n[-1] == "%":
		n = float(n[:-1]) / 100
	else:
		n = float(n)
	return max(n, x) if x is not None else n

def setup(BOT):
	BOT.add_cog(Elimpath(BOT))

class Elimpath(cmd.Cog):
	'''
	Generates an elimination path given a certain number of contestants.

	The first argument is how many people respond to round one, which defaults to 491. The second argumnt is the starting elimination rate of the TWOW, which defaults to 20%.

	The third argument is the change in the elimination rate each round. This defaults to 0. The fourth argument is the limit of the elimination rate. It will never go above or below this number depending on if the elimination rate is positive or negative. This defaults to 1.
	
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(contestants) (elim rate) (dx) (limit)"
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['elim']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="elimpath")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_elimpath(self, ctx, contestants=491, elimrate="20%", dx="0%", limit="100%"):
		'''
		Generates an elimination path with a given contestant count and elimination rate.
		'''
		await ctx.response.defer()
		await self.elimpath(ctx, contestants, elimrate, dx, limit)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def elimpath(self, ctx, contestants=491, elimrate="20%", dx="0%", limit="100%"):
		

		try: contestants = int(contestants)
		except: 
			await ctx.reply("Please enter a whole number of contestants greater than or equal to 2.", ephemeral=True)
			return

		if contestants < 2: 
			await ctx.reply("Please enter a contestant count greater than or equal to 2.", ephemeral=True)
			return

		elimrate = parse_str(elimrate, 0.00001)
		if elimrate is None:
			await ctx.reply("Please enter a valid value for the elimination rate, such as 0.2 or 20%.", ephemeral=True)

		dx = parse_str(dx, None)
		if dx is None:
			await ctx.reply("Please enter a valid value for dx, such as 0.05 or 5%.", ephemeral=True)

		limit = parse_str(limit, 0)
		if limit is None:
			await ctx.reply("Please enter a valid value for the limit, such as 0.5 or 50%.", ephemeral=True)

		rounds = []
		i = contestants
		while i > 1:
			rounds.append(i)
			i = max(1, min(i-1, i-better_round(i*elimrate)))			
			elimrate += dx
			if dx < 0: elimrate = max(limit, elimrate)
			else: elimrate = min(limit, elimrate)	
		rounds.append(1)	

		slist = rounds[:-1]
		sliced = False
		while len("'** > **".join([str(x) for x in slist])) > 1700 - len(str(contestants)):
			slist = slist[:-1]
			sliced = True
		
		if dx == 0:
			alumni_index = int((len(rounds)-1)//2)
		else:
			to_find = int(contestants**0.5//1)
			alumni_index = 0
			while rounds[alumni_index] > to_find: alumni_index += 1
			alumni_index -= 1

		plural = len(rounds) != 2

		out = f"Your TWOW will last **{len(rounds)-1}** round{'s' if plural else ''}, and here's how {'they' if plural else 'it'}'ll go:\n"
		out += f"**{'** > **'.join([str(x) for x in slist])}**{' ...' if sliced else ''} > **1**\n\n"
		out += f"Consider making **alumni-deciding** round{'s' if alumni_index != 0 else ''} {'**'+str(alumni_index)+'**' if alumni_index != 0 else ''}{' or ' if alumni_index != 0 else ''}**{alumni_index + 1}**! (Alumni count **{'** or **'.join([str(x) for x in rounds[alumni_index:alumni_index+2]])}**)"
		if dx == 0 and elimrate <= 0.05: out += "*Note that alumni counts are less accurate with lower elimination rates."
		await ctx.respond(out)
		return
			
