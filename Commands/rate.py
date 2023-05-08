from Helper.__comp import *

from Helper.__functions import plural, is_whole, smart_lookup, is_dm
from Helper.__action_functions import specify_server
from Helper.__server_functions import is_staff_here
import discord
import asyncio

def setup(BOT):
	BOT.add_cog(Rate(BOT))

class Rate(cmd.Cog):
	'''
	Reacts to a replied message and then deletes the command message. Valid arguments are one of the following seven faces: 
	XD, 
	:D, 
	:), 
	:|, 
	:/, 
	:(, 
	>:(, 
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(emote)`"
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['react','emote']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def rate(self, ctx, emote=""):
		try:
			if ctx.message.reference == None: 1/0
			reaction = {"XD":"<:6rate:1084557521953489027>",":D":"<:5rate:1084593066071052508>",":)":"<:4rate:1084556895563563028>",":|":"<:3rate:1084592150970388481>",":/":"<:2rate:1084556898470207629>",":(":"<:1rate:1084556891100815481>",">:(":"<:0rate:1084592152912347306>"}[emote]
		except ZeroDivisionError: 
			await ctx.author.send("Hey! Your usage of p!"+ctx.command.name+" did not reply to a message.")
		except: 
			await ctx.author.send("Hey! Your usage of p!"+ctx.command.name+" used an invalid emote.")
		else:
			myMsg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			await myMsg.add_reaction(reaction)
		finally:
			try: await ctx.message.delete(reason="Reaction command")
			finally: return
		return
