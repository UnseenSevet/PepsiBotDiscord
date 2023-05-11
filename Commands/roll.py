from Helper.__comp import *
from random import randint
from time import time
import discord as dc
from copy import deepcopy
from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Roll(BOT))

class Roll(cmd.Cog):
	'''
	Rolls up to 10 sets of dice specified as <count>d<value>+offset, such as 1d6 or 5d10+7. Seperate rolls via spaces or newlines.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(rolls)"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['dice']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="roll")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_roll(self, ctx, rolls = ''):
		'''
		Rolls up to 10 sets of dice specified as <count>d<value>+offset, such as 1d6 or 5d10+7.
		'''
		await ctx.response.defer()
		await self.roll(ctx, args=rolls)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def roll(self, ctx, *, args=""):
		args = args.replace("-","+-").replace("\n", " ")
		while "  " in args: args = args.replace("  ", " ")
		args = args.split(" ")[0:10]
		finalRolls = []
		outStr = ""
		total = 0
		maxval = 0
		minval = 0
		for x in args:
			try:
				count, add = x.split("d")[0:2]
				try: count = int(count)
				except: count = 1
	
				try: type, add = [int(y) for y in add.split("+")[0:2]]
				except:
					type = int(add)
					add = 0
				type = min(10000,type)
				count = min(100,count)
				adder = [[randint(1,type) for x in range(count)], add, count, type]
				total += sum(adder[0])+add
				finalRolls += [deepcopy(adder)]
				maxval += type*count
				minval += count

			except:
				continue
		if len(finalRolls) == 0:
			await ctx.respond(embed=dc.Embed(title="Error!",description="Please enter a valid roll! Rolls are formatted like 1d6, or 10d100."))
		else: 
			for x in finalRolls: 
				temp = ",".join([str(y) for y in x[0]])
				if len(temp) > 350:	temp = temp[0:350]+"..."
				outStr += f'\n**{x[2] if x[2] != 1 else ""}d{x[3]}** : {temp} {"" if x[1] == 0 else "+ "+str(x[1])}'
			outStr += f'\nTotal: **{total}**'
			try: hue = max(0,min(1,(total-minval)/(maxval-minval))*0.42)
			except: hue = 0.21
			color = dc.Colour.from_hsv(hue,.80,.80)
			print(color.r, color.g, color.b, color.value)
			e = dc.Embed(title="🎲 Rolling dice 🎲",description=outStr, color=color.value)
			avg = (maxval+minval)/2
			if avg%1 == 0: avg = int(avg)	
			e.set_footer(text=f"Maximum value: {maxval}\nAverage value: {avg}")	
			await ctx.respond(embed=e)
			
