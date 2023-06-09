from Helper.__comp import *

from time import time
from functools import partial
import random as rng

from Helper.__functions import is_slash_cmd, m_line, command_user, f_caps, plural, is_dev, is_dm
from Helper.__server_functions import is_staff, is_staff_here, member_check, is_admin
from Helper.__config import PREFIX

def setup(BOT):
	BOT.add_cog(Help(BOT))

class Help(cmd.Cog):
	'''
	Command that shows helpful info pages about the bot and its commands.

	Specifying a command or other page name using the `(command_or_page)` argument will show more 
	specific information.
	'''
	# The command user can also navigate the help pages using a dropdown menu. This menu expires 
	# after 3 minutes of activity. 


	# Extra arguments to be passed to the command
	FORMAT = "`(command_or_page)`"
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['h']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN


	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="help")
	@cmd.cooldown(1, 5)
	@cmd.check(member_check)
	async def slash_help(self, ctx,
		command_or_page = ''):
		'''
		Command that shows helpful info pages about the bot and its commands.
		'''
		await self.help(ctx, command_or_page)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def help(self, ctx,
		command_or_page = ''):
		if is_slash_cmd(ctx):
			await ctx.interaction.response.defer()
		
		all_commands = self.BRAIN.cogs
		all_commands = {
			k: v for k, v in all_commands.items() 
			if "ALIASES" in dir(self.BRAIN.get_cog(k))
		}

		found_term = False

		if command_or_page == '':
			found_term = "general_help_page"
		else:
			search_term = command_or_page.lower()

		page_options = []

		page_options.append(
			dc.SelectOption(label="General Bot Information",
			value="general_help_page", emoji="⚙️")
		)

		for cmd_n, cmd_obj in all_commands.items():
			while cmd_n[0] == "_": cmd_n = cmd_n[1:]

			page_options.append(
				dc.SelectOption(label=f"Command: {PREFIX}{cmd_n.lower()}",
				value=cmd_n, emoji=cmd_obj.EMOJI[0])
			)

			if not found_term:
				if search_term == cmd_n.lower() or search_term in cmd_obj.ALIASES:
					found_term = cmd_n.lower()

		if not found_term:
			await ctx.respond("💀 Could not find a command or category under that search term!")
			return
		
		# help_dropdown = Select(
		# 	placeholder = "Choose a category or command to get info on!",
		# 	options = page_options,
		#	custom_id = f"{command_user(ctx).id} {int(time() * 1000)}",
		#	row = 1 # Second row; leave space for page buttons in case of multi-page help text
		# )

		prev_page_button = Button(
			label = "Previous Page", emoji = "⬅️", style = dc.ButtonStyle.blurple,
			disabled = True, custom_id = f"{command_user(ctx).id} {int(time() * 1000)} p0"
		)

		next_page_button = Button(
			label = "Next Page", emoji = "➡️", style = dc.ButtonStyle.blurple, 
			custom_id = f"{command_user(ctx).id} {int(time() * 1000)} p2"
		)

		# help_dropdown.callback = self.help_page
		prev_page_button.callback = self.help_page
		next_page_button.callback = self.help_page

		full_view = View()

		# full_view.add_item(help_dropdown)
		full_view.add_item(prev_page_button)
		full_view.add_item(next_page_button)

		help_embed, full_view, display_view = await self.help_page(term=found_term,
		cmd_user=command_user(ctx), full_view=full_view)
		
		help_msg = await ctx.respond(embed=help_embed, view=display_view)

		# Update the callback to have the full message view baked in for compatibility
		cb_help = partial(self.help_page, full_view = full_view)
		# help_dropdown.callback = cb_help
		prev_page_button.callback = cb_help
		next_page_button.callback = cb_help

		await display_view.wait()
		
		await help_msg.edit(view=None)

		return
	
	async def help_page(self, ctx=None, term=None, cmd_user=None, full_view=None):
		'''
		This function serves as both a general method to make a help embed AND as a callback for 
		the interactible components in the help command
		'''

		page_n = 1
		page_total = 1

		if not ctx is None: # If this is an Interaction, find the search term + interaction data
			if 'values' in ctx.data.keys():
				term = ctx.data['values'][0]
			else:
				term = ctx.data['custom_id'].split(" ")[-1]
			
			c_id_args = ctx.data['custom_id'].split(" ")

			cmd_user_id = int(c_id_args[0])
			cmd_user = dc.utils.get(self.BRAIN.users, id=cmd_user_id)

			if ctx.user.id != cmd_user_id: # Only the command user can use the view
				await ctx.response.defer()
				return
			
			if len(c_id_args) > 3: # Get new page number from button interaction
				page_n = int(c_id_args[2][1:])

		help_embed = dc.Embed(color=0x31D8B1)
		
		full_info = self.BRAIN.cogs
		full_info = {
			k: v for k, v in full_info.items() 
			if "ALIASES" in dir(self.BRAIN.get_cog(k))
		}

		term = term.lower()
		while term[0] == "_": term = term[1:]

		if term == "general_help_page": # No term provided = general bot help
			help_embed.title = CATEGORIES["PEPSI"][0] + " **PepsiBot**"

			help_embed.description = m_line(f"""
			A Discord bot that I made mostly for fun.

			Created by <@549350426642743297>. Special thanks to <@184768535107469314> and 
			<@179686717534502913> for making the bot this is forked off of.

			**PepsiBot** supports both prefixed commands (using the prefix 
			**`{PREFIX}`**) as well as slash command versions of nearly every single command. (Commands with an asterisk do not support slash commands.)

			Use `{PREFIX}help (command/category)` for more information.
			""" # or select an option below 
			)

			help_embed.set_thumbnail(url=self.BRAIN.user.display_avatar.url)

			cmd_list = {c: [] for c in CATEGORIES.keys()}

			for cmd_n, cmd_obj in full_info.items():
				while cmd_n[0] == "_": cmd_n = cmd_n[1:]
				cmd_list[cmd_obj.CATEGORY].append(f"`{PREFIX + cmd_n.lower()}`{'*' if 'does not support slash commands' in cmd_obj.__doc__ else ''}")

			for ct, cmds in cmd_list.items():
				if len(cmds) > 0:
					help_embed.add_field(name=f"{' '.join(CATEGORIES[ct])} category", 
					value="\n".join(cmds), inline=True)

		else: # Search term is parsed as a command
			for cmd_n, cmd_obj in full_info.items():
				while cmd_n[0] == "_": cmd_n = cmd_n[1:]
				if term == cmd_n.lower() or term in cmd_obj.ALIASES:

					cmd_func = [c for c in cmd_obj.get_commands()
					if not type(c).__name__.endswith('SlashCommand')][0]

					if type(cmd_func).__name__.endswith('SlashCommandGroup'):
						cmd_func = [x for x in cmd_func.walk_commands()][0]
							

					if cmd_func.cooldown is not None:
						help_embed.add_field(name="💬 **Cooldown**", inline=True,
						value=f"{int(cmd_func.cooldown.per)} second{plural(cmd_func.cooldown.per)}"
						)
					
					if len(cmd_obj.ALIASES) != 0:
						aliases = '\n'.join([f"`{PREFIX}{a}`" for a in cmd_obj.ALIASES])
						help_embed.add_field(name="📜 **Aliases**", inline=True,
						value=aliases)

					if is_dev in cmd_func.checks:
						perm_value = "Developer"
					elif is_admin in cmd_func.checks:
						perm_value = "Administrator."
					elif is_staff in cmd_func.checks or is_staff_here in cmd_func.checks:
						perm_value = "Server Staff"
					else:
						perm_value = "Member"

					help_embed.add_field(name="👑 **Permission Level**",
					inline=True, value=perm_value)

					help_lines = m_line(cmd_obj.__doc__).replace("{PREFIX}", PREFIX)
					help_embed.title = f"▶️ **p!{term} {cmd_obj.FORMAT}**"

					cmd_lines = help_lines.split("\n\n")
					cmd_info = [""]

					for l in cmd_lines:
						if ((len(cmd_info[-1] + l + "\n\n") > 700 and cmd_info[-1] != "")
							or l == '</>'):
							cmd_info.append("")
						
						if l != '</>':
							cmd_info[-1] += l + "\n\n"
					
					page_total = len(cmd_info)
					
					help_embed.description = cmd_info[0].strip() + "\n\u200b"
					
					if page_total > 1:
						help_embed.description = cmd_info[page_n-1].strip()
						help_embed.description += (
						f"\n\n```diff\n+ Page {page_n} of {page_total} +```")
						
		
		# Flavor text partially for fun, partially to indicate who called the command
		# (Relevant since only the command user can interact with the dropdown)
		footer_text = rng.choice([
			"Nice to meet you, {}!",
			"How can I help you, {}?",
			"Hey there, {}!",
			"{} needs my help...!",
			"It's been a long time, {}. How have you been?",
			"Information be upon ye, {}!!!",
			"{} is really awesome for using this command!",
			"Thanks, {}, and have fun!",
			"What will {} look for next?",
			"0003-B: You must eat my ass {}.",
            "Beep-boop. {} requests my assistance."
		])
		
		help_embed.set_footer(text=footer_text.format(cmd_user.name),
		icon_url=cmd_user.display_avatar.url)
		
		new_items = []

		for c in full_view.children:
			c_id_args = c.custom_id.split(" ")

			if type(c).__name__ == "Select":
				if len(c_id_args) == 2:
					c_id_args.append(term)
				else:
					c_id_args[-1] = term
			
			elif type(c).__name__ == "Button":
				if len(c_id_args) == 3:
					c_id_args.append(term)
				else:
					c_id_args[-1] = term

				if c.emoji.name == "⬅️":
					c_id_args[-2] = f"p{page_n-1}"

					if page_n == 1:
						c.disabled = True
					else:
						c.disabled = False
				
				if c.emoji.name == "➡️":
					c_id_args[-2] = f"p{page_n+1}"

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
			return [help_embed, full_view, display_view]
		else:
			await ctx.response.edit_message(embed=help_embed, view=display_view)
			return
