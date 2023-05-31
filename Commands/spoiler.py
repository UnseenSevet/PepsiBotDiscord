from Helper.__comp import *
from functools import partial
from Helper.__functions import plural, is_whole, smart_lookup, is_dm, is_whole
from Helper.__action_functions import specify_server
from Helper.__server_functions import is_staff
import discord, ast, asyncio, eventlet, time
import func_timeout as ft
from evalidate import safeeval, EvalException
import ast
from random import random, randint
from math import *
def setup(BOT):
	BOT.add_cog(Spoiler(BOT))

class Spoiler(cmd.Cog):
	'''
	Generates a 49 message spoiler wall with a closing message. 
    The `template` argument will provide a template for the message to be sent in the spoiler wall. This can be anything. If you wish to make messages in the spoiler wall unique based on the message number, you can execute expressions by surrounding them with curly brackets, like `{49-x}`. The `x` variable stands for the current message number. You can use curly brackets inside expressions by first escaping them with a backslash. You can also mix plain text and expressions, like `Message #{x}`. By default, the `template` argument is `{x}`.

	In the slash command version *only*, you can specify the number of messages in the spoiler wall.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(*template)`"
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['spoilerwall']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	async def run_spoiler(self, ctx, spoiler='', message_count: int=49):
		funcs = ['str','int','len','bin', 'random', 'round', 'floor', 'ceil', 'sin', 'cos', 'range', 'randint']
		attrs = ['replace', 'join']
		nodes = ['Call', 'Attribute','Mult','Div', 'Subscript', 'Index', 'Slice', 'Load', 'Import', 'USub', 'UAdd', 'Not', 'Invert', 'List', 'Store', 'Del', 'Expr', 'Assign', 'Module', 'ListComp', 'Name', 'Constant', 'comprehension']

		message_count = max(min(100, message_count),1)

		template = spoiler
		if template.strip() == "":
			template = "{x}"

		substrings = []
		in_brackets = False
		escaped = False
		current_substring = ""
		cleaned_temp = ""
		num = 0
		for c in template:
			if c == "{" and not in_brackets and not escaped:
				in_brackets = True
				cleaned_temp += c + f'0[{num}]'
			elif c == "}" and in_brackets and not escaped:
				substrings.append(current_substring)
				num += 1
				current_substring = ""
				in_brackets = False
				cleaned_temp += c
			elif in_brackets:
				if c != "\\" or escaped:
				    current_substring += c
				else:
					cleaned_temp += c
			else:
				cleaned_temp += c
			escaped = c == "\\"

		if current_substring:
			substrings.append(current_substring)
		e = {}

		st = {'x': 0, 'random': random, 'floor': floor, 'ceil': ceil, 'sin': sin, 'cos': cos, 'pi': pi}
		for fx in range(int(message_count)):
			st['x'] = fx+1
			e = {}
			for x in range(len(substrings)):
				e[x] = 'None'
				
				try:
					e[x] = safeeval(substrings[x],st,addnodes=nodes, funcs=funcs, attrs=attrs)
				except Exception as error:
					errtype = type(error).__name__

					if errtype == 'CompilationException':
						e[x] = '{Compile error}'

					if errtype == 'ValidationException': 
						e[x] = '{Unsafe code}'
						print(ast.dump(ast.parse(substrings[x])))

					if errtype == 'ExecutionException': e[x] = '{Runtime error: '+type(error.exc).__name__+'}'

			if fx == 0:
				await ctx.reply(cleaned_temp.format(e))
			else:
				await ctx.channel.send(cleaned_temp.format(e))
			await asyncio.sleep(.5)

		await ctx.channel.send("```\nSpoiler wall closed.```")

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="spoiler")
	@cmd.cooldown(1, 15, cmd.BucketType.user)
	@cmd.check(is_staff)
	async def slash_spoiler(self, ctx, template = '', message_count: int=49):
		'''
		Generates a 49 message spoiler wall with a closing message. 
		'''
		await ctx.response.defer()
		await self.run_spoiler(ctx, spoiler=template, message_count=message_count)

		return


	@cmd.check(is_staff)
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 15, cmd.BucketType.user)
	async def spoiler(self, ctx, *, spoiler=""):
		await self.run_spoiler(ctx,spoiler=spoiler)
		return
