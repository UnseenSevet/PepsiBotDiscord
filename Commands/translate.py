from Helper.__comp import *
import json, discord, re

from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Translate(BOT))

class Translate(cmd.Cog):
	'''
	Bzzbzz bzz bzzbz bzbbzzzb, zzbbbzbzz bzzz bzz bzzz bzbzz bzzbbb zzzbzz. 
	(Translation: Input the message contents of any particular message and, if possible, it will be translated to humanspeak.)
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(mid)"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@bridge.bridge_command(aliases=ALIASES)
	@cmd.check(member_check)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	async def translate(self, ctx, *, mid):
		cleaned = re.sub("[^\w ]","",mid).lower()
		messages = json.load(open("DB/translate.json"))
		out = "Sorry, this message could not be translated from beespeak to humanspeak."
		done = False
		for x in messages.keys():
			if x in cleaned:
				out = messages[x]
				done = True
		if not done and re.sub("[BbZz ]", "", cleaned) == "":
			out = "This cannot be translated as you have not provided enough context. Please include more of the message you wish to translate."
		await ctx.reply(out)
		return
