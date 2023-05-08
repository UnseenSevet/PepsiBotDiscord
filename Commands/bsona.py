import os
from Helper.__comp import *
import re
from time import time
from Helper.__config import STARTUP
from Helper.__functions import m_line, is_dm
from Helper.__bsogen import bsona
from Helper.__functions import m_line, command_user, is_dm, is_dev
from Helper.__server_functions import is_staff_here, member_check
import discord 

def setup(BOT):
	BOT.add_cog(Bsona(BOT))

class Bsona(cmd.Cog):
	'''
	Generates a bsona for the provided name, or if not specified, the user.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(name)"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['book']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="bsona")
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_bsona(self, ctx, name=''):
		'''
		Generates a bsona for the provided name, or if not specified, the user.
		'''

		await self.bsona(ctx, name=name)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def bsona(self, ctx, *, name=''):

		if name == '': name = ctx.author.name
		wasDoubled = False
		if len(name) == 1: 
			name = name * 2
			wasDoubled = True
		bsona(name)

		states = ["California","Texas","Florida","New York","Pennsylvania","Illinois","Ohio","Georgia","North Carolina","Michigan","New Jersey","Virginia","Washington","Arizona","Tennessee","Massachusetts","Indiana","Missouri","Maryland","Wisconsin","Colorado","Minnesota","South Carolina","Alabama","Louisiana","Kentucky","Oregon","Oklahoma","Connecticut","Utah","Puerto Rico","Iowa","Nevada","Arkansas","Mississippi","Kansas","New Mexico","Nebraska","Idaho","West Virginia","Hawaii","New Hampshire","Maine","Montana","Rhode Island","Delaware","South Dakota","North Dakota","Alaska","District of Columbia","Vermont","Wyoming"]

		outname = name.lower().replace(" ", "_")
		outname = re.sub(r'\W+', '', outname)
		state = states[(ord(outname[0])-ord('a'))%26*2+(ord(outname[1])-ord('a'))%26%2]
		await ctx.reply("**"+name[0:(1 if wasDoubled else None)]+"**\n(state is "+state+")",file=discord.File("Helper/books/"+outname+".png"))
		os.remove("Helper/books/"+outname+".png")
		return
