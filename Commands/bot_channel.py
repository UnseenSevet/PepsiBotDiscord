from Helper.__comp import *

from Helper.__functions import plural, is_whole, smart_lookup, is_dm, is_whole
from Helper.__action_functions import specify_server
from Helper.__server_functions import is_staff_here, modify_server, get_server_json
import discord, re, asyncio
from func_timeout import func_timeout, FunctionTimedOut

def setup(BOT):
	BOT.add_cog(Botchannel(BOT))


class Botchannel(cmd.Cog):
	'''
	Manages the whitelist for channels members can use bot commands in. You can do add/remove/list, where add and remove add or remove channels from the whitelist, and list will make a list of all channels that are whitelisted in this server.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(add/remove/list) (channel_id)`"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['bot_channel','bot_channels','botchannels']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN


	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="botchannel")
	@cmd.cooldown(1, 1)
	@cmd.check(is_staff_here)
	async def slash_botchannel(self, ctx, mode, channel=None):
		'''
		Manages the whitelist for channels members can use bot commands in.
		'''

		await self.botchannel(ctx, mode, arg2=channel)

		return

	@cmd.check(is_staff_here)
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def botchannel(self, ctx, arg1, arg2=None):
		if is_dm(ctx):
			await ctx.reply("This command cannot be used in DMs!")
			return
		if arg1 in ['remove','add']:
			if arg2 is None:
				await ctx.respond("Please include a channel to {} the whitelist!".format(arg1+{'remove':' from','add':' to'}[arg1]))
				return
			else:
				try: arg2 = str(int(re.sub("[<#>]","",arg2)))
				except:
					await ctx.respond("Please include a valid channel to {} the whitelist!".format(arg1+{'remove':' from','add':' to'}[arg1]))
					return
				
				if int(arg2) in [x.id for x in ctx.guild.text_channels]:
					server_data = get_server_json()
					guild = server_data[str(ctx.guild.id)]
					channels = str(guild[3])
					channels = [x for x in channels.split(" ") if x != ""]
					if arg1 == 'add':
						if arg2 in channels:
							await ctx.reply("This channel is already on the whitelist!")
							return
						channels.append(arg2)
					if arg1 == 'remove': 
						if arg2 not in channels:
							await ctx.reply("This channel is not on the whitelist!")
							return
						channels.remove(arg2)
					modify_server(int(ctx.guild.id), bot = " ".join(channels))
					await ctx.reply("Whitelist succesfully modified!")
					return
				else:
					await ctx.reply("This channel does not exist in this server!")
					return
		if arg1 == 'list':
				channels = get_server_json()[str(ctx.guild.id)][3].split(" ")
				out = "**Bot whitelist**"
				for x in channels:
					out += "\n<#"+x+">"
				if out == "**Bot whitelist**": out = "No whitelisted channels."
				await ctx.reply(out)
				return
		await ctx.reply("Please input a valid subcommand! Subcommands are add, remove, and list.")

