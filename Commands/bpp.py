from Helper.__comp import *
from Helper.__bpp_parser import *
from Helper.__bpp_functions import ProgramDefinedException
import discord, os, re, time, asyncio
from Helper.__config import STARTUP
from Helper.__functions import strip_alpha, find_all, is_whole, strip_front
from Helper.__server_functions import member_check, is_dev
from datetime import datetime as dt

def setup(BOT):
	BOT.add_cog(Bpp(BOT))

class Bpp(cmd.Cog):
	'''
	Using `p!b++ run [code]` allows you to run `[code]` as B++ source code. Using `p!b++ info 
	(page)` displays a paged list of all bpp programs by use count, while using `p!b++ info (program)` 
	displays information and the source code of a specific program. `p!b++ create [program] [code]` can be used 
	to save code into a specific program name, which can be edited by its creator with `p!b++ edit [program] 
	[newcode]` or deleted with `p!b++ delete [program]`. You can check your existing programs with `p!b++ tags`. 
	Finally, `p!b++ [program] (args)` allows you to run any saved program. 
	The full documentation for all bpp program functionality is displayed in this document: 
	https://docs.google.com/document/d/1pU2ezYE505sAPEmnSMNx9yfzD7FT4_KmICOkEUpMSA8/edit?usp=sharing
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(args)"
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['bpp','tag']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="bpp")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_bpp(self, ctx, args=''):
		'''
		Run B++ code or manage a program.
		'''
		await ctx.response.defer()
		await self.bpp(ctx, args=args)

		return
	
	@cmd.command(aliases=ALIASES, name="b++")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def bpp(self, ctx, *, args=None):
		if args==None: args=""
		args = args.split(" ")
		args = [""]+[x for x in args]

		if args == ["", ""]:
			await ctx.reply("Include a subcommand!")
			return
		level = len(args)
		message = ctx.message
		if args[1].lower() == "tags":
			tag_list = get_tags(program=True,author=True,uses=True,created=True)
			
			tag_list = [tag for tag in tag_list if str(tag[2]) == str(ctx.author.id)]
			tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])
			
			# basically the same as info here
			tag_leaderboard = False
			if level == 2: # If it's not specified, assume it's the first page
				tag_list = tag_list[:10]
				page = 1
				tag_leaderboard = True
			elif is_whole(args[2]):
				if (int(args[2]) - 1) * 10 >= len(tag_list): # Detect if the page number is too big
					await ctx.reply(f"There is no page {args[2]} on your tags list!")
					return
			
				else: # This means the user specified a valid page number
					lower = (int(args[2]) - 1) * 10
					upper = int(args[2]) * 10
					tag_list = tag_list[lower:upper]
					page = int(args[2])
					tag_leaderboard = True
		
			if tag_leaderboard:
				beginning = f"```diff\nB++ Programs Page {page} for user {ctx.author.name}\n\n"

				for program in tag_list:
					r = tag_list.index(program) + 1 + (page - 1) * 10
					
					line = f"{r}{' '*(2-len(str(r)))}: {program[0]} :: {program[3]} use{'s' if program[3] != 1 else ''}"

					created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
					line += f" (written at {created_on})\n"
					beginning += line # Add this line to the final message
				
				beginning += "```" # Close off code block

				await ctx.reply(beginning)
			return
			
		if args[1].lower() == "info":
			tag_list = get_tags(program=True,author=True,uses=True,created=True,lastUsed=True)
			tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])

			tag_leaderboard = False
			if level == 2: # If it's not specified, assume it's the first page
				tag_list = tag_list[:10]
				page = 1
				tag_leaderboard = True
			
			elif is_whole(args[2]):
				if (int(args[2]) - 1) * 10 >= len(tag_list): # Detect if the page number is too big
					await ctx.reply(f"There is no page {args[2]} on the program list!")
					return
			
				else: # This means the user specified a valid page number
					lower = (int(args[2]) - 1) * 10
					upper = int(args[2]) * 10
					tag_list = tag_list[lower:upper]
					page = int(args[2])
					tag_leaderboard = True
		
			if tag_leaderboard:
				beginning = f"```diff\nB++ Programs Page {page}\n\n"

				for program in tag_list:
					r = tag_list.index(program) + 1 + (page - 1) * 10
					
					line = f"{r}{' '*(2-len(str(r)))}: {program[0]} :: {program[3]} use{'s' if program[3] != 1 else ''}"

					member_id = program[2]
					try: # Try to gather a username from the ID
						member = self.BRAIN.get_user(member_id).name
					except: # If you can't, just display the ID
						member = str(member_id)

					created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
					line += f" (written by {member} at {created_on})\n"
				
					beginning += line # Add this line to the final message
				
				beginning += "```" # Close off code block

				await ctx.reply(beginning)
				return

			tag_name = args[2]

			if tag_name not in [x[0] for x in tag_list]:
				await ctx.reply("That tag does not exist.")
				return
			
			program = tag_list[[x[0] for x in tag_list].index(tag_name)]

			member_id = program[2]
			try: # Try to gather a username from the ID
				member = ctx.guild.get_member(int(member_id)).name
			except: # If you can't, just display the ID
				member = str(member_id)
			
			created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
			c_d = dt.now() - dt.utcfromtimestamp(program[4])

			d = c_d.days
			h, rm = divmod(c_d.seconds, 3600)
			m, s = divmod(rm, 60)

			c_d = (('' if d==0 else f'{d} day{"s" if d!=1 else ""}, ') +
			('' if h==0 else f'{h} hour{"s" if h!=1 else ""}, ') +
			('' if m==0 else f'{m} minute{"s" if m!=1 else ""}, ') +
			(f'{s} second{"s" if s!=1 else ""}'))
			
			msg = f"**{program[0]}** -- by {member} -- {program[3]} use{'s' if program[3]!=1 else ''}\n"
			msg += f"Created on {created_on} `({c_d} ago)`\n"

			if program[5] != 0:
				last_used = dt.utcfromtimestamp(program[5]).strftime('%Y-%m-%d %H:%M:%S UTC')
				u_d = dt.now() - dt.utcfromtimestamp(program[5])
				
				d = u_d.days
				h, rm = divmod(u_d.seconds, 3600)
				m, s = divmod(rm, 60)

				u_d = (('' if d==0 else f'{d} day{"s" if d!=1 else ""}, ') +
				('' if h==0 else f'{h} hour{"s" if h!=1 else ""}, ') +
				('' if m==0 else f'{m} minute{"s" if m!=1 else ""}, ') +
				(f'{s} second{"s" if s!=1 else ""}'))

				msg += f"Last used on {last_used} `({u_d} ago)`\n"

			if len(program[1]) > 1700:
				fprefix = "txt"
				
				if level >= 3 and args[-1].lower() == "bpp":
					fprefix = "bpp"
				
				msg += f"The program is too long to be included in the message, so it's in the file below:"
				open(f'program_{program[0]}.{fprefix}', 'w', encoding="utf-8").write(program[1])
				await ctx.reply(msg, file=discord.File(f'program_{program[0]}.{fprefix}'))
				os.remove(f'program_{program[0]}.{fprefix}')
			else:
				msg += f"```{program[1]}```"
				await ctx.reply(msg)
			
			return


		if args[1].lower() == "create":
			if level == 2:
				await ctx.reply("Include the name of your new program!")
				return
		
			tag_name = args[2]

			if re.search(r"[^0-9A-Za-z_]", tag_name) or re.search(r"[0-9]", tag_name[0]):
				await ctx.reply(
				"Tag name can only contain letters, numbers and underscores, and cannot start with a number!")
				return
			
			if tag_name in ["create", "edit", "delete", "info", "run", "help", "tags"]:
				await ctx.reply("The tag name must not be a reserved keyword!")
				return

			if len(tag_name) > 30:
				await ctx.reply("That tag name is too long. 30 characters maximum.")
				return
			
			if level > 3:
				program = " ".join(args[3:])

			elif len(message.attachments) != 0:
				try:
					if message.attachments[0].size >= 100000:
						await ctx.reply("Your program must be under **100KB**.")
						return
					
					await message.attachments[0].save(f"DB/temp/{message.id}.txt")
					
				except Exception:
					await ctx.reply("Include a valid program to save!")
					return
				
				program = open(f"DB/temp/{message.id}.txt", "r", encoding="utf-8").read()
				os.remove(f"DB/temp/{message.id}.txt")
			
			else:
				await ctx.reply("Include a valid program to save!")
				return
			
			while program.startswith("`") and program.endswith("`"):
				program = program[1:-1]
			program.replace("{}", "\t")

			if [tag_name] in get_tags():
				await ctx.reply("There's already a program with that name!")
				return
			
			add_tag([tag_name, program, ctx.author.id, 0, time.time(), 0])
			await ctx.reply(f"Successfully created program `{tag_name}`!")
			return


		if args[1].lower() == "edit":
			if level == 2:
				await ctx.reply("Include the name of the program you want to edit!")
				return
			
			tag_name = args[2]

			tag_list = get_tags(author=True)

			if tag_name not in [x[0] for x in tag_list]:
				await ctx.reply(f"There's no program under the name `{tag_name}`!")
				return

			ind = [x[0] for x in tag_list].index(tag_name)
			if str(tag_list[ind][1]) != str(ctx.author.id) and not is_dev(ctx):
				await ctx.reply(f"You can only edit a program if you created it or if you're a dev!")
				return
			
			if level > 3:
				program = " ".join(args[3:])

			elif len(message.attachments) != 0:
				try:
					if message.attachments[0].size >= 100000:
						await ctx.reply("Your program must be under **100KB**.")
						return
					
					await message.attachments[0].save(f"DB/temp/{message.id}.txt")

				except Exception:
					await ctx.reply("Include a valid program to run!")
					return
				
				program = open(f"DB/temp/{message.id}.txt", "r", encoding="utf-8").read()
				os.remove(f"DB/temp/{message.id}.txt")
			
			else:
				await ctx.reply("Include a valid program to run!")
				return
			
			while program.startswith("`") and program.endswith("`"):
				program = program[1:-1]
			
			program = program.replace("{}", "\v")
			
			edit_tag(name=tag_name,program=program)
			await ctx.reply(f"Succesfully edited program {tag_name}!")
			return


		if args[1].lower() == "delete":
			if level == 2:
				await ctx.reply("Include the name of the program you want to delete!")
				return
			
			tag_name = args[2]

			tag_list = get_tags(author=True)

			if tag_name not in [x[0] for x in tag_list]:
				await ctx.reply(f"There's no program under the name `{tag_name}`!")
				return

			ind = [x[0] for x in tag_list].index(tag_name)
			if str(tag_list[ind][1]) != str(ctx.author.id) and not is_dev(ctx):
				await ctx.reply(f"You can only edit a program if you created it or if you're a dev!")
				return
				
			remove_tag(tag_name)
			await ctx.reply(f"Succesfully deleted program {tag_name}!")
			return


		if args[1].lower() == "run":
			if level > 2:
				program = " ".join(args[2:])

			elif len(message.attachments) != 0:
				try:
					if message.attachments[0].size >= 60000:
						await ctx.reply("Your program must be under **60KB**.")
						return

					await message.attachments[0].save(f"DB/temp/{message.id}.txt")

				except Exception:
					await ctx.reply("Include a valid program to run!")
					return
				
				program = open(f"DB/temp/{message.id}.txt", "r", encoding="utf-8").read()
				os.remove(f"DB/temp/{message.id}.txt")
			
			else:
				await ctx.reply("Include a valid program to run!")
				return

			while program.startswith("`") and program.endswith("`"):
				program = program[1:-1]
			
			program = program.replace("{}", "\v")

			program_args = []

			author = ctx.author.id

			runner = ctx.author
		
		else:
			tag_name = args[1]

			tag_list = get_tags(program=True,author=True,uses=True)

			if tag_name not in [x[0] for x in tag_list]:
				await ctx.reply(f"There's no program under the name `{tag_name}`!")
				return
			
			tag_info = [x for x in tag_list if x[0] == tag_name][0]
			program = tag_info[1]

			uses = tag_info[3] + 1
			edit_tag(name=tag_name, uses=uses, lastUsed=time.time())

			program_args = args[2:]

			author = tag_info[2]

			runner = ctx.author
			
		try:
			program_output = run_bpp_program(program, program_args, author, runner)
		except ProgramDefinedException as e:
			await ctx.reply(embed=discord.Embed(title=f'{type(e).__name__}', description=f'```{e}```'), allowed_mentions = discord.AllowedMentions.none())
			return
		except Exception as e:
			await ctx.reply(embed=discord.Embed(color=0xFF0000, title=f'{type(e).__name__}', description=f'```{e}```'), allowed_mentions = discord.AllowedMentions.none())
			return
		
		if len(program_output.strip()) == 0: program_output = "\u200b"
			
		if len(program_output) <= 2000:
			await ctx.reply(program_output, allowed_mentions = discord.AllowedMentions.none())
		elif len(program_output) <= 4096:
			await ctx.reply(embed = discord.Embed(description = program_output, type = "rich"), allowed_mentions = discord.AllowedMentions.none())
		else:
			open(f"DB/temp/{message.id}out.txt", "w", encoding="utf-8").write(program_output[:150000])
			outfile = discord.File(f"DB/temp/{message.id}out.txt")
			os.remove(f"DB/temp/{message.id}out.txt")
			await ctx.reply("⚠️ `Output too long! Sending first 150k characters in text file.`", file=outfile)
		
	
