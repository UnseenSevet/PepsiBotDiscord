from Helper.__comp import *
from random import random, randint
from time import time
from datetime import *
from Helper.__config import STARTUP
from Helper.__functions import m_line
from Helper.__server_functions import member_check
import random, os, json

def setup(BOT):
	BOT.add_cog(Respond(BOT))

async def edit(msg, text):
	try: await msg.edit(content=text)
	except: await msg.edit_original_response(content=text)
	return

class Respond(cmd.Cog):
	'''
	Generates a TWOW response via a markov chain algorithm. Increase the order for more natural words. (default is 5) 
	If you want to have a word or character limit, change type to something like 100c, or 12w, depending on what you want.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(type) (order)"
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['response']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="respond")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_respond(self, ctx, limit='10w', order=5, count=1):
		'''
		Generates a TWOW response via a markov chain algorithm.
		'''
		await ctx.response.defer()
		await self.respond(ctx, limit=limit, order=order, count=count)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def respond(self, ctx, limit="10w", order=5, count=1):

		try:
			length = min(2000,max(0,int(limit[:-1])))
			lentype = "wc"["wc".find(limit[-1])]
		except:
			length = 10
			lentype = "w"
		
		try: CHAIN_ORDER = min(100,max(1,int(order)))
		except: CHAIN_ORDER = 5

		try: count = min(10,max(1,int(count)))
		except: count = 1

		with open("Helper/Assets/responses.txt") as file:
			responses = file.readlines()

		responsesStr = "".join(responses)

		markovDict = {}
		
		chainDirs = os.listdir("Helper/Assets/chains")
		if f"chain_{CHAIN_ORDER}.json" not in chainDirs:
			msg = await ctx.reply("**Generating responses... 0% done**\n`[                    ]`")	
			percentDone = 3
			maxVal = len(responsesStr) - CHAIN_ORDER + 1
			interval = randint(80000, 120000)
			for i in range(len(responsesStr) - CHAIN_ORDER + 1):

				percentDone += 97/maxVal

				if i % interval == 0: await edit(msg,f"**Generating response{'s' if count != 1 else ''}... {round(percentDone,2)}% done**\n`[{'#' * round(percentDone/5)}{' ' * round(20-percentDone/5)}]`")

				endNum = i + CHAIN_ORDER
				
				chars = responsesStr[i : endNum]

				nextChar = (responsesStr[endNum] if endNum < len(responsesStr)
							else "\n")
				
				if chars not in markovDict:
					markovDict[chars] = [nextChar]
				else:
					markovDict[chars].append(nextChar)
			genresponses = ""

			await edit(msg,f"**Generating responses... 9{randint(8,9)}.{randint(0,9)}{randint(0,9)}% done**\n`[####################]`")
			open(f"Helper/Assets/chains/chain_{CHAIN_ORDER}.json", 'w').write(json.dumps(markovDict,indent="\t"))
		else:
			markovDict = json.load(open(f"Helper/Assets/chains/chain_{CHAIN_ORDER}.json",'r'))
			genresponses = ""
			msg = None

		for x in range(count):

			genresponse = random.choice(responses)[:CHAIN_ORDER]

			stillGoing = True

			while stillGoing:
				try:
					nextChars = markovDict[genresponse[-CHAIN_ORDER:]]
					chosenChar = random.choice(nextChars)
					if chosenChar == "\n": 
						chosenChar = " "
					genresponse += chosenChar

					if lentype == "w":
						if len(genresponse.split(" ")) > length:
							stillGoing = False
							genresponse = genresponse.strip().replace("\n", " ")
							genresponse = " ".join(genresponse.split(" ")[:length])
					if lentype == "c":
						if len(genresponse) > length+20:
							stillGoing = False
							genresponse = genresponse.strip().replace("\n", " ")
							while len(genresponse.strip()) > max(0, length-1): 
								genresponse = " ".join(genresponse.split(" ")[:-1])

					if genresponse[-1:].lower() in "abcdefghijklmnopqrstuvwxyz1234567890" and not stillGoing: 
						genresponse += "!"
				except:
					genresponse = genresponse.rstrip() + " " + random.choice(responses)[:CHAIN_ORDER]


			if genresponse == "!" and length == 0: genresponse = "⚠️ Command output is an empty string."
			genresponses += genresponse + "\n"

		if msg is not None:
			await edit(msg, genresponses[:2000])
		else:
			await ctx.reply(genresponses[:2000])
		return
