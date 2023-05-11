import os
from Helper.__comp import *
import re
from time import time
from Helper.__config import STARTUP
from Helper.__functions import m_line, is_dm
from Helper.__bsogen import bsona
from Helper.__functions import m_line, command_user, is_dm, is_dev, b64, to_base_8
from Helper.__server_functions import is_staff_here, member_check
from PIL import Image
import discord, math
import sys

def setup(BOT):
	BOT.add_cog(Fractal(BOT))

class Fractal(cmd.Cog):
	'''
	Generates a fractal based off of a given seed. You can also specify a fractal ID by starting the argument with `id=`, followed by the fractal ID.

	Seeds are generated with letters, numbers, or emojis. 

	⬛, x, 0: Empty

	⬜, w, 1: White

	🟥, r, 2: Red

	🟩, g, 3: Green

	🟦, b, 4: Blue

	🔷, c, 5: Cyan

	🟪, m, 6: Magenta

	🟨, y, 7: Yellow

	Seperate lines in the seed with newlines or spaces. Additionally, try to keep your seeds in squares so the aspect ratios remain constant.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(seed or id)"
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="fractal")
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_fractal(self, ctx, template=''):
		'''
		Generates a fractal based off of a given seed.
		'''
		await ctx.response.defer()
		await self.fractal(ctx, template=template)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)	
	async def fractal(self, ctx, *, template):
		
		template = template.replace("`","").strip().replace(" ","\n")
		MAX_XY = 1296
		if template[0:3] == "id=":
			width = int(template[3:].split(".")[-1])
			if template[3] != "c": template = bin(int(template[3:].split(".")[-2])).replace("0b","")[1:]
			else: template = ("."+to_base_8(template[3:].split(".")[-2])).replace(".0",".").replace(".1","")
			template = [[int(y) for y in template[x:x+width]] for x in range(0,len(template),width)]
			print(template)
		else: 
			colors = colors = { "0": 1,  "x": 1,  "⬛": 1,  "1": 0,  "w": 0,  "⬜": 0,  "2": 2,  "r": 2,  "🟥": 2,  "3": 3,  "g": 3,  "🟩": 3,  "4": 4,  "b": 4,  "🟦": 4,  "5": 5,  "c": 5, "🔷":5,  "6": 6,  "m": 6,  "🟪": 6,  "7": 7,  "y": 7,  "🟨": 7}
			template = [[int(colors[x.lower()]) for x in y] for y in template.splitlines(keepends=False)]
		maxw = max([len(x) for x in template])
		for x in template:
			x += [1]*(maxw-len(x))

		if template == [[0]]: template = [[0,0],[0,0]]
		if template == [[1]]: template = [[1,1],[1,1]]
		size = (len(template[0]), len(template))
		if max(size) > 36:
			await ctx.reply("Image seed too large!")
			return
		maxsize = math.floor(math.log(MAX_XY, max(size)))
		previter = Image.new("RGBA", (1, 1), color=(255, 255, 255, 255))
		for x in range(maxsize):
			size2 = [y for y in previter.size]
			x += 1
			iter = Image.new("RGBA", (size[0] * size2[0], size[1] * size2[1]), color=(0,0,0,0))
			for y in range(size[1]):
				for x in range(size[0]):
					rmult, bmult, gmult = [1,1,1]
					previter2 = previter.convert("RGB")

					if template[y][x] == 2: gmult,bmult = [0,0]
					elif template[y][x] == 3: rmult,bmult = [0,0]
					elif template[y][x] == 4: rmult,gmult = [0,0]
					elif template[y][x] == 5: rmult = 0
					elif template[y][x] == 6: gmult = 0
					elif template[y][x] == 7: bmult = 0

					Matrix = ( rmult, 0, 0, 0, 0, gmult, 0, 0, 0, 0, bmult, 0)
					previter2 = previter2.convert("RGB",Matrix)
					previter2 = previter2.convert("RGBA")
					previter2.putalpha(previter.getchannel(3))
					if template[y][x] != 1:
						iter.paste(previter2, (x * size2[0], y * size2[1]))
			previter = iter


		filenum = "1"
		for x in template:
			filenum += "".join([str(y) for y in x])
		'''
		if filenum[1:].replace("1","") == filenum[1:]:
			newdata = []
			for item in iter.getdata():
				if [x for x in item] == [0,0,0,255]:
					newdata.append((255,255,255,0))
				else:
					newdata.append(item)
			iter.putdata(newdata)
		'''
		oldnum = filenum
		base = 8
		if re.sub("[234567]","0",filenum) == filenum:
			base = 2
		if base == 2: filenum = int(filenum, base=base)
		if base == 8: filenum = b64(str(("0" if len(filenum)%2 == 1 else "") + filenum))
		if re.sub("[234567]","0",oldnum) in [42304322, 36503912]: 
			await ctx.reply("Fool me once, shame on you. Fool me twice, shame on me. Fool me three times...")
			return
		filename = "DB/fractal{}{}_{}.png".format("c_" if base == 8 else "", str(filenum)[:100], size[0])
		iter.save(filename)
		embed=discord.Embed(title="Your fractal:")
		embed.set_footer(text="id={}{}.{}".format("c." if base == 8 else "",filenum,size[0]))
		file = discord.File(filename)
		embed.set_image(url="attachment://"+filename[3:])
		await ctx.reply(embed=embed,file=file)
		os.remove(filename)
		return
