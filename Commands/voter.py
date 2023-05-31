from Helper.__comp import *
from random import randint
from time import time
import discord as dc
from copy import deepcopy
from Helper.__config import STARTUP
from Helper.__functions import m_line, is_dm
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Voter(BOT))

class Voter(cmd.Cog):
	'''
	Opens up a menu to create TWOW votes with the same algorithm as figgyc's voter website.
	(This command is in development.)
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['vote']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="voter")
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(is_dm)
	async def slash_voter(self, ctx, rolls = ''):
		'''
		Opens up a menu to create TWOW votes with the same algorithm as figgyc's voter website.
		'''
		await self.voter(ctx, args=rolls)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(is_dm)
	async def voter(self, ctx, *, args=""):
		modal = dc.ui.Modal(title="Responses")
		modal.add_item(dc.ui.InputText(label="Enter text",style=dc.InputTextStyle.long))
		modal.callback = self.modal_callback
		await ctx.send_modal(modal)


	async def modal_callback(self, interaction: dc.Interaction):
		await interaction.response.send_message(interaction.data['components'][0]['components'][0]['value'])

			
