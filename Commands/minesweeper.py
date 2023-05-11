from Helper.__comp import *

from time import time
from functools import partial
import random as rng
import discord, json, math, os, numpy
from copy import deepcopy
from Helper.__functions import is_slash_cmd, m_line, command_user, f_caps, plural, is_dev, is_dm, is_whole, is_number
from Helper.__server_functions import is_staff, is_staff_here, member_check
from Helper.__config import PREFIX
from PIL import Image, ImageOps


def setup(BOT):
	BOT.add_cog(Minesweeper(BOT))

def board_to_image(board, mouse=None):
	size = (len(board[0]),len(board))
	images = {}
	for x in ["b","f","c","x"]+[str(x) for x in range(9)]:
		images[x] = Image.open("Helper/Assets/mine/"+x+".png")
	im = Image.new("RGBA",(size[0]*16,size[1]*16))
	for x in range(size[0]):
		for y in range(size[1]):
			ttype = board[y][x]
			ftype = str(ttype[0]).lower()
			if ttype[1] == "F": ftype = "f"
			if ttype == ["B","X"]: ftype = "x"
			if ttype[1] == "C": ftype = "c"
			im.paste(images[ftype],(x*16,y*16))
	if mouse != None:
		cursor = Image.open("Helper/Assets/mine/cursor.png")
		im.paste(cursor,(mouse[1]*16,mouse[0]*16),cursor)
	rescale_factor = max(1,round(1536 / max(size)))
	im = im.resize((size[0]*rescale_factor,size[1]*rescale_factor),resample=Image.BOX)
	return im

def new_board(dm, mines):
	board = [[[0,"C"] for x in range(dm[0])] for x in range(dm[1])]
	for x in range(mines):
		while True:
			coords = [rng.randrange(0,dm[1]), rng.randrange(0,dm[0])]
			if board[coords[0]][coords[1]] != ["B","C"]:
				board[coords[0]][coords[1]] = ["B","C"]
				break
	return board


def get_game_data(userid):
	games = json.load(open("DB/ms_games.json"))
	if str(userid) not in games.keys():
		games[str(userid)] = {'board':new_board([9,9],10),'mouse':[4,4]}
		open("DB/ms_games.json","w").write(json.dumps(games,indent="\t"))
	return deepcopy(games[str(userid)])

def update_game_data(userid,board=None, mouse=None):
	get_game_data(userid)
	games = json.load(open("DB/ms_games.json"))
	temp = games[str(userid)]
	if board is not None: temp['board'] = board
	if mouse is not None: temp['mouse'] = mouse
	games[str(userid)] = temp
	open("DB/ms_games.json","w").write(json.dumps(games,indent="\t"))

async def uncover_tile(board,tile):
	height = len(board)
	length = len(board[0])
	my_tile = board[tile[0]][tile[1]]
	my_tile[1] = {"C":"U","F":"C","U":"U","X":"X"}[my_tile[1]]
	if my_tile == ["B","U"]:
		board = [[["B","U"] if x[0] == "B" else x for x in y] for y in board]
		board[tile[0]][tile[1]] = ["B","X"]
		return deepcopy(board)
	while True:
		changes = True
		for x in range(height):
			for y in range(length):
				done = False
				for v in range(max(0,x-1),min(x+2,height)):
					for w in range(max(0,y-1),min(y+2,length)):
						if board[v][w] == [0,"U"] and board[x][y][1] == "C":
							board[x][y][1] = "U"
							done = True
							changes = False
							break
					if done: break
		if changes: break
	return deepcopy(board)

async def cleanup(board,mouse):
	height = len(board)
	length = len(board[0])
	blacklist = [[v,w] for v in range(max(0,mouse[0]-1),min(mouse[0]+2,height)) for w in range(max(0,mouse[1]-1),min(mouse[1]+2,length))]

	for x in blacklist:
		if board[x[0]][x[1]] == ["B","C"]:
			board[x[0]][x[1]] = [0, "C"]
			while True:
				coords = [rng.randrange(0,height), rng.randrange(0,length)]
				if board[coords[0]][coords[1]] != ["B","C"] and [coords[0], coords[1]] not in blacklist:
					board[coords[0]][coords[1]] = ["B","C"]
					break
	for x in range(length):
		for y in range(height):
			num = 0
			for i in range(-1,2):
				for j in range(-1,2):
					if x+i in range(length) and y+j in range(height):
						num += int(board[y+j][x+i][0] == "B")
			if board[y][x][0] != "B": board[y][x][0] = num
	return board

async def handle_interaction(userid, move=None):
	desc = ""
	board_data = get_game_data(userid)
	vector_dict = {"U":(-1, 0),"D":(1, 0),"L":(0, -1),"R":(0, 1),"UR":(-1, 1),"DL":(1, -1),"UL":(-1, -1),"DR":(1, 1),"X":(0,0),"F":(0,0),None:(0,0)}
	data = deepcopy(board_data)
	board = data['board']
	mouse = data['mouse']
	movement = vector_dict[move]

	condition = 0
	if ["B","X"] not in [item for sublist in board for item in sublist]:
		mouse[0] = min(max(movement[0]+mouse[0],0),len(board)-1)
		mouse[1] = min(max(movement[1]+mouse[1],0),len(board[0])-1)
		if move == "X":
			if all([item[1] == "C" for sublist in board for item in sublist]):
				board = await cleanup(board,mouse)
			board = await uncover_tile(board,mouse)
		if move == "F":
			board[mouse[0]][mouse[1]][1] = "F"
	
	flag_count = ["CF".find(x[1]) for x in [item for sublist in board for item in sublist] if x[1] in ["C","F"]]
	mine_count = len([True for x in [item for sublist in board for item in sublist] if x[0] == "B"])

	if ["B","X"] in [item for sublist in board for item in sublist]:
		desc = f"You hit a mine. Do `p!mine new custom {len(board[0])}x{len(board)} {mine_count}` to play again!"
	if len(flag_count) == mine_count:
		desc = f"You won! Do `p!mine new custom {len(board[0])}x{len(board)} {mine_count}` to play again!"

	update_game_data(userid,board=board,mouse=mouse)
	
	showBoard = deepcopy(board)
	image = board_to_image(showBoard,mouse)
	image.save(f"DB/{userid}_ms.png")
	file = discord.File(f"DB/{userid}_ms.png")
	e = dc.Embed(color=0xC9002B,title="Minesweeper",description=desc)
	e.set_image(url=f"attachment://{userid}_ms.png")
	e.set_footer(text=f"{flag_count.count(1)}/{mine_count}",icon_url="https://media.discordapp.net/attachments/1086465868332027998/1096552706967085176/image.png")
	os.remove(f"DB/{userid}_ms.png")
	return (e, file)


class PlayView(dc.ui.View):		
	def __init__(self,author):
		self.author = author
		super().__init__()
	

		async def move_callback(interaction: dc.Interaction):
			if interaction.user.id == self.author.id:			
				c_id = interaction.data['custom_id']
				e = await handle_interaction(interaction.user.id,interaction.data['custom_id'])
				await interaction.response.edit_message(embed=e[0],file=e[1],view=PlayView(self.author))
			else: await interaction.response.defer()

		upl = dc.ui.Button(label = "", emoji = "↖️", style = dc.ButtonStyle.green, row=0, custom_id = "UL")
		upl.callback = move_callback
		self.add_item(upl)

		up = dc.ui.Button(label = "", emoji = "⬆️", style = dc.ButtonStyle.green, row=0, custom_id = "U")
		up.callback = move_callback
		self.add_item(up)

		upr = dc.ui.Button(label = "", emoji = "↗️", style = dc.ButtonStyle.green, row=0, custom_id = "UR")
		upr.callback = move_callback
		self.add_item(upr)

		left = dc.ui.Button(label = "", emoji = "⬅️", style = dc.ButtonStyle.green,row=1,custom_id = "L")
		left.callback = move_callback
		self.add_item(left)

		middle = dc.ui.Button(label = "", emoji = "⏺️", style = dc.ButtonStyle.green, row=1,custom_id = "X")
		middle.callback = move_callback
		self.add_item(middle)

		right = dc.ui.Button(label = "", emoji = "➡️", style = dc.ButtonStyle.green,row=1,custom_id = "R")
		right.callback = move_callback
		self.add_item(right)
		
		downl = dc.ui.Button(label = "", emoji = "↙️", style = dc.ButtonStyle.green,row=2,custom_id = "DL")
		downl.callback = move_callback
		self.add_item(downl)

		down = dc.ui.Button(label = "", emoji = "⬇️", style = dc.ButtonStyle.green,row=2,custom_id = "D")
		down.callback = move_callback
		self.add_item(down)
		
		downr = dc.ui.Button(label = "", emoji = "↘️", style = dc.ButtonStyle.green,row=2,custom_id = "DR")
		downr.callback = move_callback
		self.add_item(downr)

		
		flag = dc.ui.Button(label = "", emoji = "🚩", style = dc.ButtonStyle.green, row=3, custom_id = "F")
		flag.callback = move_callback
		self.add_item(flag)

class Minesweeper(cmd.Cog):
	'''
	Minesweeper is a port of the game of the same name in which you avoid mines scattered across the playing field. When you click a tile, it is uncovered and if there are mines in the immediate area around that tile (including diagonals), it will display the total number on that tile. 

	To play, do `p!minesweeper new (difficulty)`. You can specify one of the 3 default difficulties, easy medium or hard, or you can set your own board size and mine count with the `custom` difficulty! To do so, put in `custom AxB C` as your difficulty, where A and B are the dimensions of your board, and C is the number of mines.

	You can flag tiles you believe are mines with the flag button, and uncover tiles or remove flags with the central button. Be careful, as clicking a mine will cause the game to end!
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(new) (args)`"
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['mine','ms']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="minesweeper")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_minesweeper(self, ctx, args=''):
		'''
		Generates a minesweeper window.
		'''
		await ctx.response.defer()
		await self.minesweeper(ctx, args=args)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def minesweeper(self, ctx, *, args=''):

		if args != '': args = args.lower().split(" ")
		else: args = []
		args += ["",""]

		if args[0] in ['create', 'play', 'new']:
			if args[0] in ['trivial', 'baby']:
				dm = [5, 5]
				mines = 3
			elif args[1] in ['medium', 'intermediate']:
				dm = [16, 16]
				mines = 40
			elif args[1] in ['expert','hard']:
				dm = [30, 16]
				mines = 99
			elif args[1] in ['custom']:
				try:
					dm = [int(x) for x in args[2].lower().split("x")][0:2]
					mines = int(args[3])
				except:
					await ctx.respond("Invalid arguments! Please format them like '7x7 8'.")
					return
				if max(dm) > 50:
					await ctx.respond("Invalid dimensions! Maximum dimension size is 50!")
					return
				if min(dm) < 4:
					await ctx.respond("Invalid dimensions! Minimum dimension size is 4!")
					return
				if mines < 1 or mines > dm[0]*dm[1]-9:
					await ctx.respond("Invalid mine count! You must have at least 1 mine and you must allow at least 9 tiles to be safe.")
					return
			else: 
				dm = [9, 9]
				mines = 10
			board = new_board(dm,mines)
			update_game_data(ctx.author.id, board=board,mouse=[dm[1]//2,dm[0]//2])
			e = await handle_interaction(ctx.author.id)
			await ctx.respond(embed=e[0],file=e[1],view=PlayView(ctx.author))
			return

		e = await handle_interaction(ctx.author.id)
		await ctx.respond(embed=e[0],file=e[1],view=PlayView(ctx.author))
