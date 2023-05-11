from Helper.__comp import *

from Helper.__functions import plural, is_whole, smart_lookup, is_dm, is_whole, smart_lookup
from Helper.__action_functions import specify_server
from Helper.__server_functions import is_staff_here, modify_server, get_server_json, is_admin
import discord, re, asyncio

def setup(BOT):
	BOT.add_cog(Staff_role(BOT))


class Staff_role(cmd.Cog):
	'''
	Manages the list of all roles that are counted as staff roles. You can do add/remove/list, where add and remove edits the role list, and list will make a list of all roles that are whitelisted in this server.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(add/remove/list) (role)`"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['staff','staff_roles']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN


	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="staffrole")
	@cmd.cooldown(1, 1)
	@cmd.check(is_admin)
	async def slash_staff_role(self, ctx, mode, role=None):
		'''
		Manages the list of all roles that are counted as staff roles.
		'''
		await ctx.response.defer()
		await self.staff_role(ctx, mode, arg2=role)

		return

	@cmd.check(is_admin)
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def staff_role(self, ctx, arg1, *, arg2=None):
		guild = ctx.guild

		if is_dm(ctx):
			await ctx.reply("This command cannot be used in DMs!")
			return
		if arg1 in ['remove','add']:
			if arg2 is None:
				await ctx.respond("Please include a role to {} the list!".format(arg1+{'remove':' from','add':' to'}[arg1]))
				return
			else:
				server_roles = guild.roles
				get_role = smart_lookup(arg2, [r.name for r in server_roles], aliases=[str(r.id) for r in server_roles])
				try: get_role = discord.utils.get(guild.roles, name=get_role[1]).id
				except: get_role = None				
				if get_role is None:
					await ctx.respond("Could not figure out which role you wished to {} the list!".format(arg1+{'remove':' from','add':' to'}[arg1]))
					return
				get_role = str(get_role)
				server_data = get_server_json()
				guild = server_data[str(ctx.guild.id)]
				roles = guild[2]
				roles = [x for x in roles.split(" ") if x != ""]
				if arg1 == 'add':
					if get_role in roles:
						await ctx.reply("This role is already a staff role!")
						return
					roles.append(get_role)
				if arg1 == 'remove': 
					if get_role not in roles:
						await ctx.reply("This role is not on the list!")
						return
					roles.remove(get_role)
				modify_server(int(ctx.guild.id), staff = " ".join(roles))
				await ctx.reply("List succesfully modified!")
				return
		if arg1 == 'list':
				roles = get_server_json()[str(ctx.guild.id)][2].split(" ")
				out = "**Staff Roles**"
				for x in roles:
					out += "\n<@&"+x+">"
				if out == "**Staff Roles**": out = "No staff roles."
				await ctx.reply(out, allowed_mentions = discord.AllowedMentions.none())
				return
		await ctx.reply("Please input a valid subcommand! Subcommands are add, remove, and list.")

