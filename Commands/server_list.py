from Helper.__comp import *
from functools import partial
from time import time
import discord
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user
from Helper.__server_functions import is_dev, get_server_json
from math import ceil

def setup(BOT):
	BOT.add_cog(Server_list(BOT))

class Server_list(cmd.Cog):
	'''
	Returns a list of all servers the bot is in currently.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['servers']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="servers")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(is_dev)
	async def slash_server_list(self, ctx):
		'''
		Returns a list of all servers the bot is in currently.
		'''
		await ctx.response.defer()
		await self.server_list(ctx)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(is_dev)
	async def server_list(self, ctx):
		
		prev_page_button = Button(
			label = "Previous Page", emoji = "⬅️", style = dc.ButtonStyle.blurple,
			disabled = True, custom_id = f"{command_user(ctx).id} {int(time() * 1000)} p0"
		)

		next_page_button = Button(
			label = "Next Page", emoji = "➡️", style = dc.ButtonStyle.blurple, 
			custom_id = f"{command_user(ctx).id} {int(time() * 1000)} p2"
		)

		prev_page_button.callback = self.server_page
		next_page_button.callback = self.server_page

		full_view = View()

		# full_view.add_item(help_dropdown)
		full_view.add_item(prev_page_button)
		full_view.add_item(next_page_button)

		out_embed, full_view, display_view = await self.server_page(cmd_user=command_user(ctx), full_view=full_view)

		server_msg = await ctx.respond(embed=out_embed, view=display_view)

		cb_help = partial(self.server_page, full_view = full_view)
		prev_page_button.callback = cb_help
		next_page_button.callback = cb_help

		await display_view.wait()
		
		await server_msg.edit(view=None)


	async def server_page(self, ctx = None, full_view=None, cmd_user=None):


		page_n = 1
		page_total = 1

		if not ctx is None: # If this is an Interaction, find the search term + interaction data

			c_id_args = ctx.data['custom_id'].split(" ")
			await ctx.response.edit_message(embed=dc.Embed(title=f"Loading page {c_id_args[2][1:]}...", description="Please wait."))		

			cmd_user_id = int(c_id_args[0])

			if ctx.user.id != cmd_user_id: # Only the command user can use the view
				return

			cmd_user = dc.utils.get(self.BRAIN.users, id=cmd_user_id)
		
			page_n = int(c_id_args[2][1:])

		out = []
		guilds = self.BRAIN.guilds
		dat = [int(x) for x in get_server_json().keys()]
		guilds.sort(key = lambda x: len(dat) - dat.index(x.id) if x.id in dat else 1000)
		page_total = ceil(len(guilds)/20)

		for guild in guilds[page_n*20-20:page_n*20]:
			add = ""
			try: add += f"{guild.name} - {guild.owner.name}"
			except: add += f"{guild.name}"
			try:
				invite = await guild.invites()
				add += f" - {invite[0]}"
			except: pass

			out += [add]
	
		servers = discord.Embed(description="\n".join(out),title=f"Servers page {page_n} (Total {len(guilds)})")
		
		new_items = []

		for c in full_view.children:
			c_id_args = c.custom_id.split(" ")
			
			if type(c).__name__ == "Button":

				if c.emoji.name == "⬅️":
					c_id_args[-1] = f"p{page_n-1}"

					if page_n == 1:
						c.disabled = True
					else:
						c.disabled = False
				
				if c.emoji.name == "➡️":
					c_id_args[-1] = f"p{page_n+1}"

					if page_n >= page_total:
						c.disabled = True
					else:
						c.disabled = False
					
			c.custom_id = " ".join(c_id_args)

			new_items.append(c)

		# Separate a display_view from the comprehensive full_view to exclude unnecessary buttons
		display_view = View()
		full_view.clear_items()

		for c in new_items:
			full_view.add_item(c)

			if type(c).__name__ != "Button" or page_total != 1:
				display_view.add_item(c)

		if ctx is None:
			return [servers, full_view, display_view]
		else:
			await ctx.edit_original_response(embed=servers, view=display_view)
			return

