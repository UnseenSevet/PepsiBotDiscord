from Helper.__functions import command_user, is_dm, is_dev
from Helper.__config import BRAIN
import json
from random import randint

import discord as dc

def get_server_json():
	with open('DB/servers.json') as json_file:
		return json.load(json_file)

def modify_server(server_id,bot=None,staff=None,welcome=None):
	server_id = str(server_id)
	server_data = get_server_json()
	if server_id not in server_data.keys():
		server_data[server_id] = [int(server_id),0,"","",""]
	if bot is not None:
		server_data[server_id][3] = str(bot)
	if staff is not None:
		server_data[server_id][2] = str(staff)
	if welcome is not None:
		server_data[server_id][4] = str(welcome)
	open("DB/servers.json","w").write(json.dumps(server_data,indent="\t"))

def member_check(ctx, increment = True):
	value = is_dm(ctx) or is_staff_here(ctx) or is_bot_channel(ctx)

	if increment and value and not (is_dm(ctx) and command_user(ctx).id == 549350426642743297):
		increment_points(ctx)
	
	return value

def increment_points(user, amount=1):
	point_dict = json.load(open('DB/points.json'))
	user = str(command_user(user).id)
	if user not in point_dict.keys():
		point_dict[user] = amount
	else:
		point_dict[user] += amount
	open("DB/points.json","w").write(json.dumps(point_dict,indent="\t"))
	return


def is_admin(ctx):
	return ctx.author.guild_permissions.administrator or command_user(ctx) == ctx.guild.owner

def is_bot_channel(ctx):
	server_data = get_server_json()
	channels = [str(x[3]).split(" ") for x in server_data.values()]
	
	for x in channels:
		if type(ctx.channel) == dc.Thread: check_id = ctx.channel.parent_id
		else: check_id = ctx.channel.id
		if str(check_id) in x:
			return True
	if len(server_data[str(ctx.guild.id)][3]) == 0 and is_dev(ctx): return True
	return False

def member_servers(ctx):
	'''
	Returns a list of all Brain-operational servers the command user is a member of

	Useful for narrowing down where a user's server command can apply
	'''

	# server_id and member_role_id
	servers = [[s[0], s[1]] for s in get_server_json().values()]
	member_of = []

	for server_id, members_id in servers:
		server_obj = dc.utils.get(BRAIN.guilds, id=int(server_id))
		role_obj = dc.utils.get(server_obj.roles, id=int(members_id))

		if command_user(ctx) in role_obj.members:
			member_of.append(server_obj)
		elif members_id == 0 and server_obj.get_member(command_user(ctx).id) != None:
			member_of.append(server_obj)

	return member_of

def staff_servers(ctx):
	'''
	Returns a list of all Brain-operational servers the command user is staff in

	Useful for narrowing down where a user's staff command can apply (or if they can even use a 
	staff command anywhere at all)
	'''

	# The two first columns: server_id and staff_roles_id
	servers = [[s[0], s[2]] for s in get_server_json().values()]
	staff_in = []

	for s in servers:
		server_obj = dc.utils.get(BRAIN.guilds, id=int(s[0]))
		if server_obj.owner == command_user(ctx):
			staff_in.append(server_obj)
			continue
		role_obj = []
		for x in s[1].split(" "):
			if x == "": continue
			role_obj.append(dc.utils.get(server_obj.roles, id=int(x)))

		for r in role_obj:
			if command_user(ctx) in r.members:
				staff_in.append(server_obj)
	
	return staff_in

def is_staff(ctx):
	'''
	CMD module check for commands that need staff perms somewhere
	'''

	staff_in = staff_servers(ctx)

	if is_dm(ctx): # Is the member staff somewhere
		return (len(staff_in) > 0)
	else: # Is the member staff in the server
		return (ctx.guild in staff_in)

def is_staff_here(ctx):
	'''
	CMD module check for server-only commands that need staff perms in that server specifically
	'''

	return ctx.guild in staff_servers(ctx)

