import discord as dc
from discord import *
from Helper.__comp import *
from Helper.__config import TOKEN, BRAIN, STARTUP
from Helper.__functions import m_line, is_slash_cmd, get_members, command_user
from Helper.__server_functions import get_server_json, member_check, is_staff_here, modify_server, increment_points
from discord.ext import commands as cmd
from Commands.help import Help
from time import time
import os, json
import traceback as tb
from datetime import datetime

@BRAIN.event
async def on_connect():
	print(m_line(f"""PepsiBot connected to Discord at 
	{round(time() - STARTUP, 2)}s - {datetime.utcnow()}"""))

	await BRAIN.sync_commands()

@BRAIN.event
async def on_guild_join(guild):
	modify_server(guild.id)
	e = dc.Embed(title="Hello!",description="I am PepsiBot, a discord bot made for fun and for use in the TWOW community. Channels in which members can use my commands are **whitelist only**, so check out `p!bot_channel` in order to configure those. Additionally, check out `p!staff_role` to give certain roles staff permissions. ")
	e.set_thumbnail(url=BRAIN.user.display_avatar.url)
	await guild.owner.send(embed=e)
	await BRAIN.change_presence(status=dc.Status.online,
	activity=dc.Activity(type=dc.ActivityType.watching, name="{} servers with {} members".format(len(BRAIN.guilds), len(get_members(BRAIN)))))
	print(f"PepsiBot was added to server")
	print(datetime.utcnow(), "-", time())
	print(f"{guild.name} - {guild.id})")
	try: print(f"Owner is {guild.owner.name}#{guild.owner.discriminator} - {guild.owner.id}\n")
	except: pass

@BRAIN.event
async def on_guild_remove(guild):
	server_data = get_server_json()
	try: del server_data[str(guild.id)]
	except: pass
	open("DB/servers.json","w").write(json.dumps(server_data,indent="\t"))
	print(f"PepsiBot was removed from server")
	print(datetime.utcnow(), "-", time())
	print(f"{guild.name} - {guild.id})")
	try: print(f"Owner is {guild.owner.name}#{guild.owner.discriminator} - {guild.owner.id}\n")
	except: pass

@BRAIN.event
async def on_message(message):
	if message.author.bot and message.content.startswith("p!") and message.author != BRAIN.user:
		await message.reply("You must solve this CAPTCHA to prove you're not a robot:")

	await BRAIN.process_commands(message)

@BRAIN.event
async def on_member_join(member):
	try: channel = BRAIN.get_channel(int(get_server_json()[str(member.guild.id)][4]))
	except: return

	embed = dc.Embed(title=f"Welcome, {member.display_name}!",description=f"<@{member.id}> just joined **{member.guild.name}**.\n(`{member.id}`)",color=0x33dd33)
	embed.set_footer(icon_url=member.display_avatar.url, text="Enjoy your stay!")
	await channel.send(embed=embed)

@BRAIN.event
async def on_member_remove(member):
	try: channel = BRAIN.get_channel(int(get_server_json()[str(member.guild.id)][4]))
	except: return

	embed = dc.Embed(title=f"Farewell, {member.display_name}!",description=f"<@{member.id}> just left **{member.guild.name}**.\n(`{member.id}`)",color=0xdd3333)
	embed.set_footer(icon_url=member.display_avatar.url, text="We will miss you!")
	await channel.send(embed=embed)

@BRAIN.event
async def on_ready():
	print(m_line(f"""PepsiBot logged in at 
	{round(time() - STARTUP, 2)}s - {datetime.utcnow()}"""), '\n')

	restart_rep_sv = None
	restart_rep_ch = None
	restart_rep_t = None

	for arg in sorted(sys.argv):
		if arg.startswith("1_report_guild:"):
			if arg[len("1_report_guild:"):] == "":
				continue
			
			restart_rep_sv = dc.utils.get(BRAIN.guilds,
				id=int(arg[len("1_report_guild:"):]))

		if arg.startswith("2_report_chnl:"):
			if restart_rep_sv is None:

				for guild in BRAIN.guilds:
					try:
						restart_rep_ch = guild.get_member(int(arg[len("2_report_chnl:"):]))

					except dc.errors.NotFound:
						continue
				
			else:
				restart_rep_ch = dc.utils.get(restart_rep_sv.channels,
					id=int(arg[len("2_report_chnl:"):]))

		if arg.startswith("3_report_time:"):
			restart_rep_t = int(arg[len("3_report_time:"):])/1000
		
	if restart_rep_t is not None and restart_rep_ch is not None:
		t_taken = round(time() - restart_rep_t, 2)
		try: await restart_rep_ch.send(
			f"✅ **Successfully restarted PepsiBot** in {t_taken}s.\n")
		except: pass

	print("="*50, '\n')

	await BRAIN.change_presence(status=dc.Status.online,
	activity=dc.Activity(type=dc.ActivityType.watching, name="{} servers with {} members".format(len(BRAIN.guilds), len(get_members(BRAIN)))))

	for cog_name in BRAIN.cogs:
		cog_obj = BRAIN.get_cog(cog_name)

		# Check for a task/event that could have a setting to be turned on while connecting
		if not "ON_BY_DEFAULT" in dir(cog_obj) or not "set_loop" in dir(cog_obj):
			continue
		
		getattr(cog_obj, "ON_BY_DEFAULT")
		
		if getattr(cog_obj, "ON_BY_DEFAULT"):
			getattr(cog_obj, "set_loop")(True)
			print(f"Automatically starting all loops in {type(cog_obj).__name__.upper()}")
	
	print("\n" + "="*50, '\n')

@BRAIN.event
async def on_command_error(ctx, error): # For prefixed commands
	await error_handler(ctx, error)

@BRAIN.event
async def on_application_command_error(ctx, error): # For slash commands
	await error_handler(ctx, error)

async def error_handler(ctx, err):
	if type(err) == cmd.errors.CommandNotFound:
		if member_check(ctx, False) or is_staff_here(ctx): await ctx.respond(f"💀 This command or alias does not exist!")
		return
	
	if type(err) in [cmd.errors.MissingRequiredArgument, cmd.errors.ArgumentParsingError]:
		help = Help(BRAIN)
		help_embed, full_view, display_view = await help.help_page(term=ctx.command.name, cmd_user=command_user(ctx), full_view = View())
		await ctx.respond(embed=help_embed)
		increment_points(ctx, -1)
		return
	
	if type(err) in [dc.errors.CheckFailure, cmd.errors.CheckFailure]:
		if member_check(ctx, False) or is_staff_here(ctx): await ctx.respond("💀 You do not have permission to run this command!")
		if not member_check(ctx, False) and is_slash_cmd(ctx): await ctx.respond("💀 You do not have permission to run this command here!", ephemeral=True)
		return
	
	if type(err) == cmd.errors.CommandOnCooldown:
		if is_slash_cmd(ctx):
			await ctx.respond("🐌 **This command is on cooldown right now!**", ephemeral=True)
		else:
			await ctx.message.add_reaction("🐌")
		increment_points(ctx, -1)
		return
	
	print("-[ERROR]- "*10)
	tb.print_exception(type(err), err, None)

	if type(err).__name__ == "CommandInvokeError":
		err = err.original

	try:
		await ctx.respond(
		f"💀 Uh oh! This command raised an error: **`{type(err).__name__}`**")
		increment_points(ctx, -1)
	except Exception as e:
		print(f"\nCouldn't inform user of error due to {type(e).__name__}!")
		increment_points(ctx, -1)
	
	print("-[ERROR]- "*10, '\n')

@BRAIN.event
async def on_command(ctx):
	print("Text command from", ctx.message.author)
	print(datetime.utcnow(), "-", time())

	try:
		print(ctx.message.channel.name, f"({ctx.message.channel.id})")
		print(ctx.message.guild.name, f"({ctx.message.guild.id})")
	except AttributeError:
		print("Sent in DMs")
	
	print("-->", ctx.message.content, "\n")

@BRAIN.event
async def on_application_command(ctx):
	print("Slash command from", ctx.user)
	print(datetime.utcnow(), "-", time())

	try:
		print(ctx.channel.name, f"({ctx.channel.id})")
		print(ctx.guild.name, f"({ctx.guild.id})")
	except AttributeError:
		print("Sent in DMs")
	
	print(f"--> /{ctx.command}\n")
	
print("="*50, '\n')

commands_loaded = []

for cmd_name in os.listdir("Commands"):
	if not cmd_name.endswith('py') or cmd_name.startswith('__'):
		continue

	BRAIN.load_extension(f"Commands.{cmd_name[:-3]}")

	commands_loaded.append(cmd_name[:-3].upper())

print(f"Added the following commands: {', '.join(commands_loaded)}", '\n')

print("="*50, '\n')

tasks_loaded = []

for task_name in os.listdir("Tasks"):
	if not task_name.endswith('py') or task_name.startswith('__'):
		continue

	BRAIN.load_extension(f"Tasks.{task_name[:-3]}")

	tasks_loaded.append(task_name[:-3].upper())

print(f"Loaded in the following tasks: {', '.join(tasks_loaded)}", '\n')

print("="*50, '\n')

token = open("DB/token.txt",'r').read()
BRAIN.run(token)

