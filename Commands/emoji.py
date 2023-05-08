from Helper.__comp import *

from time import time
import discord as dc
from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Emoji(BOT))

class Emoji(cmd.Cog):
	'''
	Returns helpful information about a custom server emoji.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(emoji)"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="emoji")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_emoji(self, ctx, emoji=None):
		'''
		Generates a emoji for the provided name, or if not specified, the user.
		'''

		await self.emoji(ctx, emoji=emoji)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def emoji(self, ctx, emoji=None):
		if emoji == None:
			await ctx.respond("Please provide a custom emoji to get information on!")
			return
		emoji = dc.PartialEmoji.from_str(emoji)
		if not emoji.is_custom_emoji():
			await ctx.respond("Please provide a custom emoji to get information on!")
			return
		e = dc.Embed(title="Emoji Information",description=f"Name: [{emoji.name}]({emoji.url}) {str(emoji)}\nID: `{emoji.id}`")
		e.set_thumbnail(url=emoji.url)
		await ctx.respond(embed=e)
		return
