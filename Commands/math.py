from Helper.__comp import *
import cexprtk, math, random, discord

from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(Math(BOT))

class Math(cmd.Cog):
	'''
	Using this command will evaluate the arguments provided as a mathematical or logical expression. 
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['calc', 'eval']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="math")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_math(self, ctx, expression=''):
		'''
		Using this command will evaluate the arguments provided as a mathematical or logical expression. 
		'''
		await ctx.response.defer()
		await self.math(ctx, expression=expression)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def math(self, ctx, *, expression=''):
		if expression == '':
			await message.channel.send("Please enter a mathematical expression to evaluate.")
			return
		
		try:
			expression_string = expression.strip()
			while expression_string.startswith("`") and expression_string.endswith("`"):
				expression_string = expression_string[1:-1]

			expression_string = expression_string.replace("while","#####")
				
			st = cexprtk.Symbol_Table(variables={"e": math.e, "phi": (1 + math.sqrt(5))/2},add_constants=True, functions={"rand":random.uniform})
			e = cexprtk.Expression(expression_string, st)
			output = e.value()
			if output % 1 == 0: output = int(output)
			else: output = round(output,15)
			
			if math.isnan(output) and len(e.results()) != 0: output = str(e.results())[1:-1]
			
			await ctx.reply(embed=discord.Embed(title=f"Expression result:", description=str(output)[:2000]))
		except Exception as e:
			await ctx.reply("There was an error in parsing your statement.")
			print(str(e))
		return
