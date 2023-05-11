from Helper.__comp import *
import json
import os
import sys
from time import time
from datetime import datetime

from Helper.__server_functions import member_check
from Helper.__functions import m_line, command_user, is_dm, is_dev, get_members

def setup(BOT):
	BOT.add_cog(Top(BOT))


class Top(cmd.Cog):
	'''
	Lists server members sorted by the amount of PepsiBot commands they've used. To see the global list, do `p!top global`. 
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "PEPSI"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['lb']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN


	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="top")
	@cmd.cooldown(1, 8, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_top(self, ctx, page=1, is_global: bool=False):
		'''		
		Lists server members sorted by the amount of PepsiBot commands they've used.
		'''
		await ctx.response.defer()

		if is_global: 
			await self.top(ctx, "global", page)
		else:
			await self.top(ctx, page)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 8, cmd.BucketType.user)
	@cmd.check(member_check)
	async def top(self, ctx, arg1=1, arg2=None):

		is_global = str(arg1).lower() == "global"
		
		point_dict = json.load(open('DB/points.json'))

		if is_global: page = int(arg2)
		else: page = int(arg1)

		page -= 1

		is_global = is_global or is_dm(ctx)
	
		keys = point_dict.keys()

		if is_global:
			member_list = sorted([[x.name, point_dict[str(x.id)] if str(x.id) in keys else 0, x.id] for x in get_members(self.BRAIN)], key=lambda x: x[1], reverse=True)
		else:
			member_list = sorted([[x.name, point_dict[str(x.id)] if str(x.id) in keys else 0, x.id] for x in ctx.guild.members], key=lambda x: x[1], reverse=True)

		myID = command_user(ctx).id
		out = f"You are rank `#{[member_list.index(s) for s in member_list if s[2] == myID][0]+1}` {'globally' if is_global else 'in this server'}\nwith a total of **{[s[1] for s in member_list if s[2] == myID][0]}** command usages.\n"
		for x in member_list[page*10:page*10+10]:
			out += f"`{x[0]}{(32-len(x[0]))*' '}{(7-len(str(x[1])))*' '}{x[1]}`\n"

		if len(member_list[page*10:page*10+10]) == 0:
			out = f"There is no page {page+1} of the command user list!"
			
		
		e = dc.Embed(title=f"Global command usage - page {page+1}" if is_global else f"Command usage by **{ctx.guild.name}** members - page {page+1}", description=out)

		await ctx.respond(embed=e)

		return
