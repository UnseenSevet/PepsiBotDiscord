from Helper.__comp import *
from time import time
from random import choice
import json
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user, is_dm
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Rst(BOT))

class Rst(cmd.Cog):
	'''
	Chooses a random string submitted to the rst (randomly selected text) database (by default, only from the current guild.) To add text, run the command `p!rst add` followed by whatever you wish to add. If you wish to select text submitted to all servers, run the command `p!rst global`.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(args)"
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="rst")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_rst(self, ctx, args=''):
		'''
		Picks a random string submitted to the rst (randomly selected text) database.
		'''

		await self.rst(ctx, args=args)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def rst(self, ctx, *, args="get"):
		mode = args.split(" ")[0].lower()

		db = json.load(open("DB/rst.json"))
		
		if mode == "get":
			options = [x[0] for x in db] if is_dm(ctx) else [x[0] for x in db if x[1] == ctx.guild.id]
			if len(options) == 0: out = "The RST database for this server is empty! Be the first person to add something with `p!rst add`."
			else: out = choice(options)

		elif mode == "global":
			options = [x[0] for x in db]
			out = choice(options)

		elif mode == "add":
			text = " ".join(args.split(" ")[1:])			
			if len(text) > 1950:
				out = ":skull: Maximum entry length is 1950 characters!"
			else:
				db += [[text, ctx.guild.id, command_user(ctx).id]]
				open("DB/rst.json","w").write(json.dumps(db,indent="\t"))
				out = "Text successfully added!"

		await ctx.respond(out)

		return
