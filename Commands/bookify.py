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

def is_hex(s):
	return re.sub("^#[0-9A-Fa-f]{6}$", s, "") == ""

def setup(BOT):
	BOT.add_cog(Bookify(BOT))

class Bookify(cmd.Cog):
	'''
	Generates a book out of the attatched image. If you wish, you can also add a face by doing `p!bookify [face color]`.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(face_color)"
	CATEGORY = "TWOW"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="bookify")
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_bookify(self, ctx, file: dc.Attachment, face_color = 'none'):

		if face_color[0] != "#": face_color = "#"+face_color
		await ctx.response.defer()
		image = file

		try: 
			path = f"Helper/Assets/{ctx.user.id}{image.filename}"
			await image.save(path)
			image = Image.open(path).convert("RGBA")
			os.remove(path)
		except:
			ctx.reply("Please attach a proper image, as this could not be converted to a PNG.", ephemeral=True)

		limbs = Image.open(f"Helper/Assets/Book/book_overlay.png")
		face = Image.open(f"Helper/Assets/Book/face_overlay.png")
		bg = Image.open("Helper/Assets/Book/cover_overlay.png")
	
		if face_color != '#none':
			set_color = "#ffffff"
			if face_color.lower() == 'black': set_color = "#000000"
			if is_hex(face_color):
				set_color = face_color
			else:
				if face_color.lower() not in ['black, white']: 
					await ctx.respond("Please specify face color with a hex code in the form of `#000000`, `black`, or `white`. Defaulting to white...",ephemeral=True)

			mask = Image.new("RGBA", (1080,1080), set_color)
			face = Image.composite(Image.new("RGBA", (1080,1080), (0,0,0,0)), mask, face)

		image = image.resize((730,810), resample=Image.BOX)

		temp = Image.new('RGBA', (1080, 1080), (255,255,255,255))
		temp.paste(image,(176,51),image)

		bg = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), temp, bg)

		bg = Image.alpha_composite(bg,limbs)
		if face_color != '#none': bg = Image.alpha_composite(bg,face)

		path = f'Helper/books/{ctx.user.id}.png'
		bg.save(path,"PNG")

		await ctx.reply("**Image bookified!**",file=discord.File(path))
		os.remove(path)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5, cmd.BucketType.user)
	@cmd.check(member_check)
	async def bookify(self, ctx, face_color = 'none'):

		if face_color[0] != "#": face_color = "#"+face_color
		image = None

		attachments = ctx.message.attachments
		for x in attachments:
			if x.content_type.split("/")[0] == "image":
				path = f"Helper/Assets/{ctx.message.id}{x.filename}"
				try: 
					await x.save(path)
					image = Image.open(path).convert("RGBA")
				except: pass				
				try: os.remove(path)
				except: pass

		if image == None and ctx.message.reference != None:
			msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			attachments = msg.attachments
			for x in attachments:
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
	
		limbs = Image.open(f"Helper/Assets/Book/book_overlay.png")
		face = Image.open(f"Helper/Assets/Book/face_overlay.png")
		bg = Image.open("Helper/Assets/Book/cover_overlay.png")
	
		if face_color != '#none':
			set_color = "#ffffff"
			if face_color.lower() == 'black': set_color = "#000000"
			if is_hex(face_color):
				set_color = face_color
			else:
				if face_color.lower() not in ['black, white']: 
					await ctx.respond("Please specify face color with a hex code in the form of `#000000`, `black`, or `white`. Defaulting to white...",ephemeral=True)

			mask = Image.new("RGBA", (1080,1080), set_color)
			face = Image.composite(Image.new("RGBA", (1080,1080), (0,0,0,0)), mask, face)

		image = image.resize((730,810), resample=Image.BOX)

		temp = Image.new('RGBA', (1080, 1080), (255,255,255,255))
		temp.paste(image,(176,51),image)

		bg = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), temp, bg)

		bg = Image.alpha_composite(bg,limbs)
		if face_color != '#none': bg = Image.alpha_composite(bg,face)

		path = f'Helper/books/{ctx.message.id}.png'
		bg.save(path,"PNG")

		await ctx.reply("**Image bookified!**",file=discord.File(path))
		os.remove(path)
		return
