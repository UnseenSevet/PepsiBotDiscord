import os
from Helper.__comp import *
import re
from time import time
from Helper.__config import STARTUP
from Helper.__functions import m_line, is_dm
from Helper.__bsogen import bsona
from Helper.__functions import m_line, command_user, is_dm, is_dev
from Helper.__server_functions import is_staff_here, member_check
import discord 
from PIL import Image, ImageDraw, ImagePath, ImageOps
import math
import re
import colorsys
import os

def setup(BOT):
	BOT.add_cog(Bookify(BOT))

class Bookify(cmd.Cog):
	'''
	Generates a book out of the attatched image. If you wish, you can also add a face by doing `p!bookify True`.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(face)"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="bookify")
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_bookify(self, ctx, image: dc.Attachment, face: bool = False):

		await ctx.response.defer()

		try: 
			path = f"Helper/Assets/{ctx.user.id}{image.filename}"
			await image.save(path)
			image = Image.open(path).convert("RGBA")
		except:
			ctx.reply("Please attach a proper image, as this could not be converted to a PNG.", ephemeral=True)

		limbs = Image.open(f"Helper/Assets/Book/{'book' if face else 'faceless'}_overlay.png")
		bg = Image.open("Helper/Assets/Book/cover_overlay.png")

		image = image.resize((730,810), resample=Image.BOX)

		temp = Image.new('RGBA', (1080, 1080), (255,255,255,255))
		temp.paste(image,(176,51),image)

		bg = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), temp, bg)

		bg = Image.alpha_composite(bg,limbs)

		path = f'Helper/books/{ctx.user.id}.png'
		bg.save(path,"PNG")

		await ctx.reply("**Image bookified!**",file=discord.File(path))
		os.remove(path)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def bookify(self, ctx, face=False):

		image = None

		attatchments = ctx.message.attachments
		for x in attatchments:
			if x.content_type.split("/")[0] == "image":
				path = f"Helper/Assets/{ctx.message.id}{x.filename}"
				try: 
					await x.save(path)
					image = Image.open(path).convert("RGBA")
				except: pass				
				try: os.remove(path)
				except: pass

		if image == None:
			await ctx.respond("Could not convert any attatchments to PNG. Please attatch a suitable image.")
			return
	
		limbs = Image.open(f"Helper/Assets/Book/{'book' if face else 'faceless'}_overlay.png")
		bg = Image.open("Helper/Assets/Book/cover_overlay.png")

		image = image.resize((730,810), resample=Image.BOX)

		temp = Image.new('RGBA', (1080, 1080), (255,255,255,255))
		temp.paste(image,(176,51),image)

		bg = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), temp, bg)

		bg = Image.alpha_composite(bg,limbs)

		path = f'Helper/books/{ctx.message.id}.png'
		bg.save(path,"PNG")

		await ctx.reply("**Image bookified!**",file=discord.File(path))
		os.remove(path)
		return
