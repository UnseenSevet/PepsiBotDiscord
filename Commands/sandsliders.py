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


indices = ["S",1,2,14,3,4,5,6,7,8,9,10,11,12,13,16,17,18,19,"L"]
t_options = [
	["Sand","<:sand:1095052138742288464>","S"],
	["Wall","<:wall:1095052144333299762>",1],
	["Goal","<:goal:1095051970798178425>",2],
	["Death","<:death:1095051966134104186>",14],
	["Crumble (1)","<:crumb1:1095051963516854322>",3],
	["Crumble (2)","<:crumb2:1095051965580451870>",4],
	["One-way (Up)","<:up:1095051984664526938>",5],
	["One-way (Down)","<:down:1095051968852009000>",6],
	["One-way (Left)","<:left:1095051976363999433>",7],
	["One-way (Right)","<:right:1095052136452206603>",8],
	["Dotted line block","<:dotted:1095051967715360858>",9],
	["Dotted line block (Filled)","<:filled:1095108520799633559>",10],
	["Two-state switch","<:switch0:1095561967390965760>",11],
	["Two-state (Blue)","<:tb0:1095052140541657139>",12],
	["Two-state (Red)","<:tr1:1095052142420689109>",13],
	["Key","<:key:1095563162654351410>",16],
	["Key wall","<:keywall:1095051973826449438>",17],
	["Blue portal","<:portal1:1095051977358069882>",18],
	["Orange portal","<:portal2:1095052135831457802>",19],
	["Lead","<:lead:1095469970118422600>","L"],
	]
options = []
for x in t_options:
	options.append(dc.SelectOption(label=x[0],value=str(x[2]),emoji=x[1]))

def set_transparency(im,x):
	im = im.copy()
	datas = im.getdata()
	newData = []
	for item in datas:
		if item[3] == 255:
			if rng.random() < 0.08: newData.append((0,0,0,0))
			else: newData.append(tuple(list(item[0:3])+[x]))
		else:
			newData.append(item)
	im.putdata(newData)
	return im

def MAX_LEVEL(): 
	levels = json.load(open("DB/ss_levels.json")).keys()
	return len([val for val in levels if is_whole(val)])

def setup(BOT):
	BOT.add_cog(Sandsliders(BOT))

def board_to_image(board_data, trail=[],move=None, mouse=None):
	state = deepcopy(board_data['state'])
	board = deepcopy(board_data['board'])
	if len(trail):
		trailim = Image.open("Helper/Assets/sand/trail.png")
		if move in ["U","D"]:
			trailim = trailim.rotate(90)

	board = [[1]*(len(board[0])+2)]+[[1]+x+[1] for x in board]+[[1]*(len(board[0])+2)]
	size = (len(board[0]),len(board))
	images = {
		"S":"sand",
		"L":"lead",
		0:"ground",
		1:"wall",
		2:"goal",
		14:"death",
		3:"crumb1",
		4:"crumb2",
		5:"up",
		6:"down",
		7:"left",
		8:"right",
		9:"dotted",
		10:"filled",
		11:"switch{}".format(state),
		12:"tb{}".format(state),
		13:"tr{}".format(state),
		16:"key",
		17:"keywall",
		18:"portal1",
		19:"portal2",
	}
	altwall = Image.open("Helper/Assets/sand/wall2.png")
	for x in images.keys():
		images[x] = Image.open("Helper/Assets/sand/"+images[x]+".png")
	im = Image.new("RGBA",(size[0]*16,size[1]*16))
	for x in range(size[0]):
		for y in range(size[1]):
			paste = images[board[y][x]]
			if board[y][x] == 1:
				surround = True
				for i in range(-1,2):
					for j in range(-1,2):
						try: 
							if board[y+j][x+i] != 1: surround = False
						except: 
							pass
						if y+j not in range(size[1]) or x+i not in range(size[0]): surround = False
				if surround: paste = altwall
			im.paste(paste,(x*16,y*16))
	trail = [x for x in trail if board[x[0]+1][x[1]+1] in [0,2,5,6,7,8]]
	for x in range(len(trail)):
		y = trail[x]
		y = [y[0]+1,y[1]+1]
		if rng.randint(0,1) == 0: trailim = trailim.rotate(180)
		try: alpha = int((x/(len(trail)))*150+70)
		except: alpha = 220
		to_paste = trailim
		if len(trail[x]) == 3:
			to_paste = to_paste.convert("LA").convert("RGBA")
		to_paste = set_transparency(to_paste,alpha)
		im.paste(to_paste,(y[1]*16,y[0]*16),to_paste)
	if mouse != None:
		cursor = Image.open("Helper/Assets/sand/cursor.png")
		im.paste(cursor,(mouse[1]*16+16,mouse[0]*16+16),cursor)
	rescale_factor = max(1,math.floor(1024 / max(size)))
	im = im.resize((size[0]*rescale_factor,size[1]*rescale_factor),resample=Image.BOX)
	return im

def move_board(board_data,dirVec):
	gameBoard, sands, state = deepcopy(board_data)
	trail = []
	done = [False] * len(sands)
	momentum = [0] * len(sands)
	dead = False
	size = (len(gameBoard),len(gameBoard[0]))
	sands.sort(key = lambda x: x[0 if dirVec[0] else 1])
	if sum(dirVec) == 1:
		sands = sands[::-1]

	while not (dead or all(done)):
		for q in range(len(sands)):
			x = sands[q]
			trail.append(x.copy())
			if dirVec[0]+x[0] not in range(size[0]) or dirVec[1]+x[1] not in range(size[1]) or [dirVec[0]+x[0],dirVec[1]+x[1]] in [x[0:2] for x in sands] or done[q]:
				done[q] = True
				continue
			mtype = deepcopy(gameBoard)[dirVec[0]+x[0]][dirVec[1]+x[1]]

			if mtype in [18, 19]:
				foundPortal = False
				for i in range(size[0]):
					for j in range(size[1]):
						if deepcopy(gameBoard)[i][j] == mtype and [dirVec[0]+x[0], dirVec[1]+x[1]] != [i,j] and [i,j] not in [x[0:2] for x in sands] and not foundPortal:
							x[0] = i
							x[1] = j
							foundPortal = True
							momentum[q] += 1
				if not foundPortal:
					mtype = 1

			if mtype in range(5,9):
				if dirVec == {5:(-1, 0),6:(1, 0),7:(0, -1),8:(0, 1)}[mtype]:
					mtype = 0
				else:
					mtype = 1

			if mtype == [12,13][state]:
				mtype = 1

			if mtype == [12,13][1-state]:
				mtype = 0

			if mtype == 11:
				if momentum[q]: state = 1-state
				done[q] = True

			if mtype in [1,10,17]:
				done[q] = True

			if mtype == 16:
				gameBoard[dirVec[0]+x[0]][dirVec[1]+x[1]] = 0
				if all([16 not in x for x in gameBoard]):
					gameBoard = [[0 if y == 17 else y for y in x] for x in gameBoard]
				
			if mtype == 9:
				gameBoard[dirVec[0]+x[0]][dirVec[1]+x[1]] = 10

			if mtype == 14: 
				if len(x) == 2:
					sands.pop(q)
					dead = True
					break
				else: mtype = 0

			if mtype in [0,9,2,15,16]: 
				x[0] += dirVec[0]
				x[1] += dirVec[1]
				momentum[q] += 1

			if mtype == 3:
				if momentum[q]: gameBoard[dirVec[0]+x[0]][dirVec[1]+x[1]] = 4
				done[q] = True

			if mtype == 4:
				if momentum[q]: 
					gameBoard[dirVec[0]+x[0]][dirVec[1]+x[1]] = 0
					x[0] += dirVec[0]
					x[1] += dirVec[1]
				else: done[q] = True
		if max(momentum) >= 100:
			dead = True
	if dead:
		return ('d',deepcopy([gameBoard, sands, state]),max(momentum),trail)
	elif all([2 == gameBoard[x[0]][x[1]] or len(x) == 3 for x in sands]) and (all([16 not in x for x in gameBoard]) or not all([17 not in x for x in gameBoard])):
		return ('w',deepcopy([gameBoard, sands, state]),max(momentum),trail)
	return (None,deepcopy([gameBoard, sands, state]),max(momentum),trail)


def data_to_code(game_data):
	board, sands, state = deepcopy(game_data)
	if all([len(x) != 2 for x in sands]):
		return "COMPILE ERROR: No sand"
	if len(sands) > 10:
		return "COMPILE ERROR: Too many physics objects (sand/lead)"
	if sum(x.count(18) for x in board) not in [0,2]:
		return "COMPILE ERROR: Invalid number of blue portals"
	if sum(x.count(19) for x in board) not in [0,2]:
		return "COMPILE ERROR: Invalid number of orange portals"

	base81 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()+-:;<=>?@[]^"
	ternaryString = "1"
	for x in board:
		for y in x:
			ternaryString += "{:0>3}".format(numpy.base_repr(y,base=3))
	while len(ternaryString) % 4 != 0:
		ternaryString = "0" + ternaryString
	base81String = ""
	for x in range(0,len(ternaryString),4):
		base81String += base81[int(ternaryString[x:x+4],base=3)]
	out = base81String+"."+str(len(board[0]))+"."+"//".join(["/".join([str(y) for y in x]) for x in sands])+"."+str(state)
	out = out.replace("00","}").replace("}}","{")
	return out

def code_to_data(code):
	code = code.replace("*","").replace("{","}}").replace("}","00").replace("-","/")
	datas = code.split(".")
	datas[1] = int(datas[1])
	base81 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()+-:;<=>?@[]^"
	ternaryString = ""
	for x in datas[0]:
		ternaryString += "{:0>4}".format(numpy.base_repr(base81.find(x), base=3))
	ternaryString = ternaryString[ternaryString.find("1") + 1:]
	blocks = [int(ternaryString[x:x + 3], base=3) for x in range(0, len(ternaryString), 3)]
	board = [blocks[x:x + datas[1]] for x in range(0, len(blocks), datas[1])]
	sands = [[int(y) if is_number(y) else y for y in x.split("/")] for x in datas[2].split("//")]
	return [board, sands, int(datas[-1])]


def get_game_data(userid):
	games = json.load(open("DB/ss_games.json"))
	if str(userid) not in games.keys():
		games[str(userid)] = {'board':[],'sands':[],'level':0.5,'moves':"",'state':0,'undos':[]}
		open("DB/ss_games.json","w").write(json.dumps(games,indent="\t"))
	return deepcopy(games[str(userid)])

def update_game_data(userid,board=None,sands=None,level=None,moves=None,state=None,undos=None):
	get_game_data(userid)
	games = json.load(open("DB/ss_games.json"))
	temp = games[str(userid)]
	if board is not None: temp['board'] = board
	if sands is not None: temp['sands'] = sands
	if level is not None: temp['level'] = level
	if moves is not None: temp['moves'] = moves
	if state is not None: temp['state'] = state
	if undos is not None: temp['undos'] = undos
	games[str(userid)] = temp
	open("DB/ss_games.json","w").write(json.dumps(games,indent="\t"))

def get_editor(userid):
	games = json.load(open("DB/ss_editor.json"))
	if str(userid) not in games.keys():
		games[str(userid)] = {'board':[[0]],'sands':[],'mouse':[0,0,1]}
		open("DB/ss_editor.json","w").write(json.dumps(games,indent="\t"))
	return deepcopy(games[str(userid)])

def update_editor(userid,board=None,sands=None,mouse=None):
	get_editor(userid)
	games = json.load(open("DB/ss_editor.json"))
	temp = games[str(userid)]
	if board is not None: temp['board'] = board
	if sands is not None: temp['sands'] = sands
	if mouse is not None: temp['mouse'] = mouse
	games[str(userid)] = temp
	open("DB/ss_editor.json","w").write(json.dumps(games,indent="\t"))

def get_level(level):
	games = json.load(open("DB/ss_levels.json","r"))
	if is_number(level):
		return [games[str(level)]['board'],games[str(level)]['sands']]
	else:
		return code_to_data(level)[0:2]

def handle_interaction(userid, move=None):
	board_data = get_game_data(userid)
	vector_dict = {"U":(-1, 0),"D":(1, 0),"L":(0, -1),"R":(0, 1)}
	data = deepcopy(board_data)
	sands = data['sands']
	gameBoard = data['board']
	level = data['level']
	moves = data['moves']
	state = data['state']
	undos = data['undos']
	title = "Level {}".format(level)
	trail = []
	oldMoves = moves
	try: move = move.upper()
	except: pass

	if is_number(level):
		if level % 1 == 0.5: move = None
		if move is not None:
			temp = move_board([gameBoard,sands,state],vector_dict[move])
			trail = temp[3]
			if temp[2]: 
				moves += move
				undos.append((data_to_code([gameBoard,sands,state]),level))
			if temp[0] == 'd':		
				title = "YOU DIED! Press any button to try again."
				level -= 0.5
			elif temp[0] == 'w':
				if level == MAX_LEVEL():
					title = "YOU BEAT THE GAME! Press any button to go back to level 1."
					level = 0.5
				else:
					level += 0.5
					title = "LEVEL COMPLETE! Press any button to continue."	
			gameBoard, sands, state = temp[1]
		else:
			if level % 1 == 0.5:
				level = int(level + 0.5)
				gameBoard, sands = get_level(level)
				state = 0
				undos = []
				moves = ""
				title = "Level {}".format(level)
		footer = "Moves: "+moves.split("X")[-1]
	else:
		title = "Custom Level"
		if level[0] == "*": move = None
		if move is not None:
			temp = move_board([gameBoard,sands,state],vector_dict[move])
			trail = temp[3]
			if temp[2]: 
				moves += move
				undos.append((data_to_code([gameBoard,sands,state]),level))
			if temp[0] == 'd':
				title = "YOU DIED! Press any button to try again."
				level = "*"+level
			elif temp[0] == 'w':
				title = "LEVEL COMPLETE! Press any button to try again."
				level = "*"+level
			gameBoard, sands, state = temp[1]
		else:
			if level[0] == "*":
				level = level[1:]
				gameBoard, sands = code_to_data(level)[0:2]
				state = 0
				moves = ""
				undos = []
		footer = level.replace("*","")+"\n\nMoves: "+moves.split("X")[-1]

		

	update_game_data(userid,board=gameBoard,sands=sands,level=level,moves=moves,state=state,undos=undos)
	
	showBoard = deepcopy(gameBoard)
	for x in sands:
		showBoard[x[0]][x[1]] = "S" if len(x) == 2 else "L"
	send_data = get_game_data(userid)
	send_data['board'] = showBoard
	image = board_to_image(send_data,move=move,trail=trail)
	image.save("DB/{}_ss.png".format(userid))
	file = discord.File("DB/{}_ss.png".format(userid))
	e = dc.Embed(color=0xC9002B,title=title,description="This command is currently in development.")
	e.set_image(url="attachment://"+str(userid)+"_ss.png")
	e.set_footer(text=footer)
	os.remove("DB/{}_ss.png".format(userid))
	return (e, file)

def handle_edit(userid, move=None):
	editor = deepcopy(get_editor(userid))
	vector_dict = {"U":(-1, 0),"D":(1, 0),"L":(0, -1),"R":(0, 1),"X":(0, 0),"Z":(0, 0)}
	sands = editor['sands']
	editorBoard = editor['board']
	mouse = editor['mouse']

	if move is not None:
		movement = vector_dict[move]
		mouse[0] = min(max(movement[0]+mouse[0],0),len(editorBoard)-1)
		mouse[1] = min(max(movement[1]+mouse[1],0),len(editorBoard[0])-1)
		
		if move == "Z":
			if mouse[0:2] in sands: sands.remove(mouse[0:2])
			if mouse[0:2]+["L"] in sands: sands.remove(mouse[0:2]+["L"])
			editorBoard[mouse[0]][mouse[1]] = 0
		elif move == "X":
			if mouse[2] == "S":
				sands = [x for x in sands if len(x) != 2]
				sands += [mouse[0:2]]
				editorBoard[mouse[0]][mouse[1]] = 0
			elif mouse[2] == "L":
				if mouse[0:2] in sands: sands.remove(mouse[0:2])
				if mouse[0:2]+["L"] in sands: sands.remove(mouse[0:2]+["L"])
				sands += [mouse[0:2]+["L"]]
				editorBoard[mouse[0]][mouse[1]] = 0
			else:
				if mouse[0:2] in sands: sands.remove(mouse[0:2])
				if mouse[0:2]+["L"] in sands: sands.remove(mouse[0:2]+["L"])
				editorBoard[mouse[0]][mouse[1]] = (mouse[2] if move != "Z" else 0)
		
		update_editor(userid,board=editorBoard,sands=sands,mouse=mouse)

	footer = data_to_code([editorBoard,sands,0])
	footer += "\n\nSelected: "+t_options[indices.index(mouse[2])][0]
	footer += f"\nLocation: {mouse[1]+1}, {mouse[0]+1}"	

	showBoard = deepcopy(editorBoard)
	for x in sands:
		showBoard[x[0]][x[1]] = "S" if len(x) == 2 else "L"
	image = board_to_image({'board':showBoard,'state':0},mouse=mouse)
	image.save("DB/{}_sse.png".format(userid))
	file = discord.File("DB/{}_sse.png".format(userid))
	e = dc.Embed(color=0xC9002B,title="Editing level...")
	e.set_image(url="attachment://"+str(userid)+"_sse.png")
	e.set_footer(text=footer)
	os.remove("DB/{}_sse.png".format(userid))
	return (e, file)

class EditView(dc.ui.View):
	def __init__(self,author):
		self.author = author
		super().__init__()

		async def confirm_callback(interaction: dc.Interaction):
			if interaction.data['components'][0]['components'][0]['value'].lower() == "yes":
				board = get_editor(self.author.id)['board']
				update_editor(userid=self.author.id,board=[[0]*len(board[0])]*len(board),sands=[])
				e = handle_edit(self.author.id)
				await interaction.response.edit_message(embed=e[0],file=e[1],view=EditView(self.author))
			else: await interaction.response.defer()
		
		self.confirm = dc.ui.Modal(title="Confirm wipe? (YES/NO)")
		self.confirm.add_item(dc.ui.InputText(label="This action cannot be undone."))
		self.confirm.callback = confirm_callback

		async def goto_callback(interaction: dc.Interaction):
			value = interaction.data['components'][0]['components'][0]['value'].replace(","," ")
			while "  " in value: value = value.replace("  "," ")
			location = [int(x)-1 for x in value.split(" ")][0:2][::-1]
			temp = get_editor(self.author.id)
			location[0] = min(max(0,location[0]),len(temp['board']))
			location[1] = min(max(0,location[1]),len(temp['board'][0]))
			cursor = temp['mouse']
			update_editor(userid=self.author.id, mouse=location+[cursor[2]])
			e = handle_edit(self.author.id)
			await interaction.response.edit_message(embed=e[0],file=e[1],view=EditView(self.author))
				
		
		self.goto = dc.ui.Modal(title="Input coordinates: (x, y)")
		self.goto.add_item(dc.ui.InputText(label=""))
		self.goto.callback = goto_callback

		async def reset_callback(interaction: dc.Interaction):
			if interaction.user.id != self.author.id: await interaction.response.defer()
			await interaction.response.send_modal(self.confirm)

		async def goto_b_callback(interaction: dc.Interaction):
			if interaction.user.id != self.author.id: await interaction.response.defer()
			await interaction.response.send_modal(self.goto)

		async def move_callback(interaction: dc.Interaction):
			if interaction.user.id == self.author.id:			
				c_id = interaction.data['custom_id']
				e = handle_edit(interaction.user.id,c_id)
				await interaction.response.edit_message(embed=e[0],file=e[1],view=EditView(self.author))
			else: await interaction.response.defer()
		
		async def select_callback(interaction: dc.Interaction):
			if interaction.user.id == self.author.id:
				block = interaction.data['values'][0]
				if is_whole(block): block = int(block)
				mouse = get_editor(self.author.id)['mouse']
				mouse[2] = block
				update_editor(userid=self.author.id,mouse=mouse)
			await interaction.response.defer()

		remove = dc.ui.Button(label = "", emoji = "<:eraser:1095568970611953804>", style = dc.ButtonStyle.red, row=0, custom_id = "Z")
		remove.callback = move_callback
		self.add_item(remove)

		up = dc.ui.Button(label = "", emoji = "⬆️", style = dc.ButtonStyle.red, row=0, custom_id = "U")
		up.callback = move_callback
		self.add_item(up)

		self.add_item(dc.ui.Button(label = "", emoji = "<:x:1068668773713850378>", style = dc.ButtonStyle.grey, row=0,disabled = True,))

		left = dc.ui.Button(label = "", emoji = "⬅️", style = dc.ButtonStyle.red,row=1,custom_id = "L")
		left.callback = move_callback
		self.add_item(left)

		middle = dc.ui.Button(label = "", emoji = "⏺️", style = dc.ButtonStyle.red, row=1,custom_id = "X")
		middle.callback = move_callback
		self.add_item(middle)

		right = dc.ui.Button(label = "", emoji = "➡️", style = dc.ButtonStyle.red,row=1,custom_id = "R")
		right.callback = move_callback
		self.add_item(right)

		goto_b = dc.ui.Button(label = "Goto", style = dc.ButtonStyle.red,row=2)
		goto_b.callback = goto_b_callback
		self.add_item(goto_b)

		down = dc.ui.Button(label = "", emoji = "⬇️", style = dc.ButtonStyle.red,row=2,custom_id = "D")
		down.callback = move_callback
		self.add_item(down)
		
		self.add_item(dc.ui.Button(label = "", emoji = "<:x:1068668773713850378>", style = dc.ButtonStyle.grey, row=2,disabled = True,))
	
		reset = dc.ui.Button(label = "Wipe", style = dc.ButtonStyle.red,row=3)
		reset.callback = reset_callback
		self.add_item(reset)

		select = dc.ui.Select(
			placeholder = "Select a block type!",
			options = options,
			row = 4)
		select.callback = select_callback
		self.add_item(select)

class PlayView(dc.ui.View):		
	def __init__(self,author):
		self.author = author
		super().__init__()
	

		async def move_callback(interaction: dc.Interaction):
			if interaction.user.id == self.author.id:			
				c_id = interaction.data['custom_id']
				if c_id != "X": e = handle_interaction(interaction.user.id,interaction.data['custom_id'])
				else: e = handle_interaction(interaction.user.id)
				await interaction.response.edit_message(embed=e[0],file=e[1],view=PlayView(self.author))
			else: await interaction.response.defer()

		async def undo_callback(interaction: dc.Interaction):
			if interaction.user.id == self.author.id:
				game_data = get_game_data(interaction.user.id)
				undos = game_data['undos']
				if len(undos) == 0:
					await interaction.response.defer()
					return
				undo = undos.pop(-1)
				board,sands,state = code_to_data(undo[0])
				level = undo[1]
				update_game_data(interaction.user.id,board=board,sands=sands,state=state,undos=undos,moves=game_data['moves'][0:-1],level=level)
				e = handle_interaction(interaction.user.id)
				await interaction.response.edit_message(embed=e[0],file=e[1],view=PlayView(self.author))
			else: await interaction.response.defer()

		async def reset_callback(interaction: dc.Interaction):
			if interaction.user.id != self.author.id:
				await interaction.response.defer()
			else:
				try:			
					level = get_game_data(interaction.user.id)
					gameBoard, sands = get_level(level['level'])
					undos = level['undos']
					undos.append((data_to_code([level['board'],level['sands'],level['state']]),level['level']))
					update_game_data(interaction.user.id,board=gameBoard,sands=sands,moves=level['moves']+"X",state=0, undos=undos)
				except: pass
				e = handle_interaction(interaction.user.id)
				await interaction.response.edit_message(embed=e[0],file=e[1],view=PlayView(self.author))


		undo = dc.ui.Button(label = "", emoji = "↩️", style = dc.ButtonStyle.red, row=0)
		undo.callback = undo_callback
		self.add_item(undo)

		up = dc.ui.Button(label = "", emoji = "⬆️", style = dc.ButtonStyle.red, row=0, custom_id = "U")
		up.callback = move_callback
		self.add_item(up)

		self.add_item(dc.ui.Button(label = "", emoji = "<:x:1068668773713850378>", style = dc.ButtonStyle.grey, row=0,disabled = True,))

		left = dc.ui.Button(label = "", emoji = "⬅️", style = dc.ButtonStyle.red,row=1,custom_id = "L")
		left.callback = move_callback
		self.add_item(left)

		middle = dc.ui.Button(label = "", emoji = "⏺️", style = dc.ButtonStyle.red, row=1,custom_id = "X")
		middle.callback = move_callback
		self.add_item(middle)

		right = dc.ui.Button(label = "", emoji = "➡️", style = dc.ButtonStyle.red,row=1,custom_id = "R")
		right.callback = move_callback
		self.add_item(right)
		
		self.add_item(dc.ui.Button(label = "", emoji = "<:x:1068668773713850378>", style = dc.ButtonStyle.grey, row=2,disabled = True,))

		down = dc.ui.Button(label = "", emoji = "⬇️", style = dc.ButtonStyle.red,row=2,custom_id = "D")
		down.callback = move_callback
		self.add_item(down)
		
		reset = dc.ui.Button(label = "", emoji = "🔄", style = dc.ButtonStyle.red, row=2)
		reset.callback = reset_callback
		self.add_item(reset)

class Sandsliders(cmd.Cog):
	'''
	Sandsliders is a puzzle game by pepsi#1213 where you move your character (a sand block) in a specific direction, with the goal of getting to the end.
	
	The arrow buttons will move your player, the 🔄 button resets the level, and the ↩️ button will undo your last move. The center button acts the same as running the command `p!sand` by itself, but without creating a new message.

	The current levels are **for testing purposes**, meaning they are not very interesting puzzles. The levels will eventually be replaced.

	You can play a campaign level with `p!sand` (which will pull up your current save), and if you want to play a specific level you can do `p!sand level [num]`. However, there is also a **level editor** that lets you build and play your own levels!

	In order to create a level, do `p!sand create AxB` where A and B are the dimensions of your level. The level editor menu will then be opened where you can place blocks anywhere on the screen via your cursor. The four arrow buttons move your cursor around, and :record_button: will place the currently selected block. The <:eraser:1095568970611953804> button will erase the block your cursor is on, and you can also wipe or manually reposition your cursor with the Wipe or Goto buttons.

	If your current message expires while making a level, don't worry! Your progress has been saved, and you can load it back up with `p!sand editor`. Once you want to actually play your level, you can do `p!sand load [code]`, where code is the level code that's shown below your level as you're editing it. Note that loading a custom level will reset your progress if you're playing a campaign level, and you'll have to do `p!sand level [num]` to go back.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(args)`"
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['sand','sandslider','sands']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.slash_command(name="sandsliders")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_sandsliders(self, ctx, args=''):
		'''
		Generates a sandsliders window.
		'''
		await ctx.response.defer()
		await self.sandsliders(ctx, args=args)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def sandsliders(self, ctx, *, args=''):

		if args[0] in ['level','load','import','play']:
			if len(args) > 1 or args[0] == 'level':
				if args[1] in json.load(open("DB/ss_levels.json")).keys():
					try:
						get_game_data(ctx.author.id)
						update_game_data(userid=ctx.author.id,level=int(args[1])-0.5)
					except: pass
				else:
					try: 
						game_data = code_to_data(args[1])
					except: pass
					else:
						update_game_data(userid=ctx.author.id,level="*"+(args[1].replace("*","")),board=game_data[0],sands=game_data[1],state=0)
			else:
				data = get_editor(ctx.author.id)
				update_game_data(userid=ctx.author.id,level="*"+data_to_code([data['board'],data['sands'],0]),board=data['board'],sands=data['sands'],state=0)

			e = handle_interaction(ctx.author.id)
			await ctx.respond(embed=e[0],file=e[1],view=PlayView(ctx.author))
			return

		if args[0] == 'create':
			try:
				dimensions = [int(x) for x in args[1].lower().split("x")][0:2]
			except:
				await ctx.respond("Invalid dimensions! Please format them like '7x7'.")
				return
			if max(dimensions) > 30:
				await ctx.respond("Invalid dimensions! Maximum dimension size is 30!")
				return
			if min(dimensions) < 1:
				await ctx.respond("Invalid dimensions! Minimum dimension size is 1!")
				return

			update_editor(ctx.author.id, board=[[0]*dimensions[0]]*dimensions[1],sands=[],mouse=[dimensions[1]//2,dimensions[0]//2,1])
			e = handle_edit(ctx.author.id)
			await ctx.respond(embed=e[0],file=e[1],view=EditView(ctx.author))
			return
		if args[0] in ['edit','editor']:
			try:
				data = code_to_data(args[1])
				update_editor(ctx.author.id, board=data[0],sands=data[1],mouse=[0,0,1])
			except: pass
			e = handle_edit(ctx.author.id)
			await ctx.respond(embed=e[0],file=e[1],view=EditView(ctx.author))
			return	
	
		if args[0] == 'editor_code':
			data = get_editor(ctx.author.id)
			await ctx.respond(data_to_code([data['board'],data['sands'],0]))
			return

		e = handle_interaction(ctx.author.id)
		await ctx.respond(embed=e[0],file=e[1],view=PlayView(ctx.author))
