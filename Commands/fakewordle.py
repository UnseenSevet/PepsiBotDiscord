from Helper.__comp import *
from random import random
from time import time
from datetime import *
from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Fakewordle(BOT))

class Fakewordle(cmd.Cog):
	'''
	Generates fake Wordle results.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="fakewordle")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_fakewordle(self, ctx):
		'''
		Generates fake Wordle results.
		'''
		await ctx.response.defer()
		await self.fakewordle(ctx)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def fakewordle(self, ctx):
		d0 = date(2021, 6, 19)
		d1 = date.today()
		dt = int((d1 - d0).total_seconds()//86400)
		myGuess = [0,0,0,0,0]
		guesses = []
		for x in range(6):
			for y in range(5):
				if myGuess[y] == 1: myGuess[y] = 0
				if random() < x/7 and myGuess[y] == 0:
					myGuess[y] = 2
			for y in range(5):
				if random() < 0.3 and myGuess[y] == 0:
					myGuess[y] = 1
			guesses += ["".join(["⬛🟨🟩"[y] for y in myGuess])]
			if myGuess == [2,2,2,2,2]: break
		outStr = "Wordle "+str(dt)+" "+(str(len(guesses)) if myGuess == [2,2,2,2,2] else "X")+"/6\n"
		for x in guesses:
			outStr += x+"\n"
		await ctx.reply(outStr)
		return
