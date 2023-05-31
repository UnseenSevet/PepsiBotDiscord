from Helper.__comp import *

from time import time
import discord as dc
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user, is_dm
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Me(BOT))

class Me(cmd.Cog):
	'''
	Checks the Discord API for all the information about you.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="me")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_me(self, ctx):
		'''
		Checks the Discord API for all the information about you.
		'''
		await ctx.response.defer()
		await self.me(ctx)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def me(self, ctx, emoji=None):
		me = command_user(ctx)
		e = dc.Embed(title=f"{me.name}#{me.discriminator}")
		e.set_image(url=me.display_avatar.url)
		text = m_line(f'''/n/
		id: {me.id}/n/
		display_name: {me.display_name}/n/
		color: {me.color.to_rgb()}/n/
		created_at: {me.created_at}/n/
		''')
		if is_dm(ctx): text += f"mutual_guilds: `{'`, `'.join([x.name for x in me.mutual_guilds])}`"
		else: text += "mutual_guilds: **This can only be viewed in DMs.**"
		e.description=text

		await ctx.respond(embed=e)
		return
