import os
from Helper.__comp import *
import re
from time import time
from Helper.__config import STARTUP
from Helper.__functions import m_line, is_dm
from Helper.__functions import m_line, command_user, is_dm, is_dev, is_whole
from Helper.__server_functions import is_staff_here, member_check
import discord 
from PIL import Image, ImageDraw, ImagePath, ImageOps
import math, re, colorsys, os, cexprtk, random, numpy
from scipy import special


def is_hex(s):
	return re.sub("^#[0-9A-Fa-f]{6}$", s, "") == ""

def setup(BOT):
	BOT.add_cog(Desmos(BOT))

def ln(x): return math.log(x)

def factorial(x): return math.gamma(x)

def mod(a,b): return a%b

def fill(a,b):
	return (a,b)[num]

def lamb(a):
	if numpy.imag(special.lambertw(a)) == 0: return numpy.real(special.lambertw(a))

#smarter function parser
def parse_funcs(s):
	s = s.replace("π",'pi').replace('\n',' ') 
	while "  " in s: s = s.replace('  ',' ')
	expressions = '+*^%/'
	funcList = []
	currFunc = ' '
	in_p = 0
	s = s.strip()+" "
	for nx in range(len(s)):
		x = s[nx]
		if x == "(": in_p += 1
		if x == ")": in_p -= 1
		if x == ' ' and in_p == 0 and currFunc[-1] not in expressions+'-' and x not in expressions and (s+" ")[nx+1] not in expressions:
			funcList += [ppp(currFunc)]
			currFunc = ' '
		elif x != ' ':
			currFunc += x.lower()
	if currFunc != ' ':
		funcList += [ppp(currFunc)]

	return funcList

#parse potential paramatetic
def ppp(s):
	s = s.strip().replace("while","#####")
	out = None

	if s[0] == "(" and s[-1] == ")":
		out = []
		currFunc = ''
		in_p = 0
		s = s[1:-1]+","
		for nx in range(len(s)):
			x = s[nx]
			if x == "(": in_p += 1
			if x == ")": in_p -= 1
			if x == ',' and in_p == 0:
				out.append(currFunc)
				currFunc = ''
			else:
				currFunc += x
	else: out = s 
	return out


class Desmos(cmd.Cog):
	'''
	Graphs up to 8 functions of x, or just 1 equation in terms of both x and y. You can specify the scale of the graph, or set the x/y offsets to shift the graph around by any amount (by default, 0). Graphs of functions can be `y=x^2`, for example, but `x^2+y^2=1` would be a graph of an equation. 

	If you wish to specify multiple functions, make sure to seperate them with a space. In order to do this on a text command, surround all the functions with quotes, like `"x^2 sin(x)"`. List of functions supported by this command: https://pastebin.com/ev79QPxC

	
	'''

	# Extra arguments to be passed to the command
	FORMAT = "[functions] (scale) (x_offset) (y_offset) (experimental)"
	CATEGORY = "UTILITY"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['graph', 'graphing']

	global num
	num = 0




	def __init__(self, BRAIN):
		self.BRAIN = BRAIN
		self.added_funcs = {"rand":random.uniform, 'gamma':factorial, 'fill':fill, 'lambertw':lamb, 'ln':ln, 'truemod':mod}


	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="desmos")
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_desmos(self, ctx, functions, scale="1.0", x_offset="0.0", y_offset="0.0"):
		print(functions)

		'''
		Graphs up to 8 functions of x, or 1 equation of both x and y. 
		'''
		await ctx.response.defer()
		await self.desmos(ctx, functions=functions, scale=scale, x_offset=x_offset, y_offset=y_offset)
		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3, cmd.BucketType.user)
	@cmd.check(member_check)
	async def desmos(self, ctx, functions, scale="1.0", x_offset="0.0", y_offset="0.0"):
		funcraw = functions

		try:
			x_offset = float(x_offset)
			y_offset = float(y_offset)
			scale = float(scale)
		except:
			raise cmd.errors.ArgumentParsingError()
		scale = scale*2
		


		functions = [(x.replace("y=" if x[:2] == 'y=' else " ","") if type(x) == str else x) for x in parse_funcs(functions)[:8]]
		colors = ["#dd4444", "#44dd44", "#4444dd", "#44dddd", "#dd44dd", "#dddd44", "#dddddd", '#444444']

		st = cexprtk.Symbol_Table(variables={"x":0, "e":math.e, 'phi':(1+5**0.5)/2},add_constants=True, functions=self.added_funcs)

		graph = Image.new("RGBA", (500,500), (0,0,0,0))
		draw = ImageDraw.Draw(graph)


		magnitude = 10**(math.ceil(math.log10(scale/(2)))-1)

		movement = (50*magnitude)/scale
		hasThin = movement > 7
		if hasThin:
			startPos = (math.floor((-250*(scale/50)+x_offset)/magnitude)*magnitude-x_offset)*50/scale+250
			while startPos <= 500:
				draw.rectangle([(round(startPos),0),(round(startPos)+1,499)],fill='#80808040')
				startPos += movement

			startPos = 499-((math.ceil((250*(scale/50)+y_offset)/magnitude)*magnitude-y_offset)*50/scale+250)
			while startPos <= 500:
				draw.rectangle([(0,round(startPos)),(499,round(startPos)+1)],fill='#80808040')
				startPos += movement

		magnitude = float(magnitude*10)
		movement = (50*magnitude)/scale

		if hasThin: 
			thickColor = '#90909060'
		else:
			thickColor = '#80808040'

		startPos = (math.floor((-250*(scale/50)+x_offset)/magnitude)*magnitude-x_offset)*50/scale+250
		while startPos <= 500:
			draw.rectangle([(round(startPos)-1,0),(round(startPos)+2,499)],fill=thickColor)
			startPos += movement

		startPos = 499-((math.ceil((250*(scale/50)+y_offset)/magnitude)*magnitude-y_offset)*50/scale+250)
		while startPos <= 500:
			draw.rectangle([(0,round(startPos)-1),(499,round(startPos)+2)],fill=thickColor)
			startPos += movement

		draw.rectangle([(248-int(x_offset*50/scale),0),(253-int(x_offset*50/scale),499)],fill="#ffffff")
		draw.rectangle([(0, 248 +int(y_offset*50/scale)),(499, 253+int(y_offset*50/scale))],fill="#ffffff")

		funcnames = ' '

		for func_num in range(len(functions)):
			global num
			function = functions[func_num]


			domain_issues = False
			oldCoords = None

			ftype = "cartesian"


			if type(function) == list:
				ftype = 'param'
				try: 
					st = cexprtk.Symbol_Table(variables={"t":0, "e":math.e, 'phi':(1+5**0.5)/2},add_constants=True,functions=self.added_funcs)
					e = [cexprtk.Expression(function[0], st), cexprtk.Expression(function[1], st)]
				except:
					await self.desmos_experimental(ctx, functions=funcraw,scale=scale, x_offset=x_offset, y_offset=y_offset)
					return

			else:
				try: 
					st = cexprtk.Symbol_Table(variables={"x":0, "e":math.e, 'phi':(1+5**0.5)/2},add_constants=True,functions=self.added_funcs)
					e = cexprtk.Expression(function, st)
				except cexprtk.ParseException:
					st = cexprtk.Symbol_Table(variables={"theta":0, "e":math.e, 'phi':(1+5**0.5)/2},add_constants=True,functions=self.added_funcs)
					if function[:2] == "r=": function = function[2:]
					try:
						e = cexprtk.Expression(function, st)
					except cexprtk.ParseException:
						await self.desmos_experimental(ctx, functions=funcraw,scale=scale, x_offset=x_offset, y_offset=y_offset)
						return
					ftype = 'polar'

			if ftype == 'param':
				funcadd = f"`({','.join(function)})`"
			else:
				funcadd = f"`{'r' if ftype == 'polar' else 'y'}="+function+'`'

			funcnames += ("**, and** " if func_num == len(functions)-1 and len(functions) != 1 else "**, **")+funcadd


			if ftype == 'polar':
				pixel = Image.new("RGBA", (2, 2), colors[func_num])
				in_theta = -5*math.pi*scale
				while in_theta < 5*math.pi*scale:
					num = 1-num
					in_theta += 0.01*scale
					st.variables['theta'] = in_theta

					try:
						out_r = e.value()
						in_x = out_r*math.cos(in_theta)
						in_y = out_r*math.sin(in_theta)
						check_x = max(-1000, min(1500, round(((in_x-x_offset)*50/scale)+250)))
						check_y = max(-1000, min(1500, 500-round(((in_y-y_offset)*50/scale)+250)))
					except:
						domain_issues = True
						oldCoords = None
						continue

					try: diff = max(abs(check_x - oldCoords[0]),abs(check_y - oldCoords[1]))
					except: diff = 0

					if diff > 2000:
						oldCoords = None

					graph.paste(pixel,(check_x-1, check_y-1))

					if oldCoords != None: draw.line([(check_x+1, check_y),oldCoords],fill=colors[func_num],width=5)
					
					oldCoords = (check_x+1, check_y)

			elif ftype == 'param':
				pixel = Image.new("RGBA", (2, 2), colors[func_num])
				for check_t in range(5001):
					num = check_t%2
					in_t = ((check_t-500)*scale)/50
					st.variables['t'] = in_t

					try:
						in_x = e[0].value()
						in_y = e[1].value()
						check_x = max(-1000, min(1500, round(((in_x-x_offset)*50/scale)+250)))
						check_y = max(-1000, min(1500, 500-round(((in_y-y_offset)*50/scale)+250)))
					except:
						oldCoords = None
						domain_issues = True
						continue
			
					try: diff = max(abs(check_x - oldCoords[0]),abs(check_y - oldCoords[1]))
					except: diff = 0

					if diff > 2000:
						oldCoords = None

					graph.paste(pixel,(check_x-1, check_y-1))

					if oldCoords != None: draw.line([(check_x+1, check_y),oldCoords],fill=colors[func_num],width=5)
					
					oldCoords = (check_x+1, check_y)


			else:
				pixel = Image.new("RGBA", (4, 4), colors[func_num])
				for check_x in range(501):
					num = check_x%2
					in_x = (check_x - 250)*(scale/50)+x_offset
					st.variables['x'] = in_x
					try: 
						check_y = 500-round(((e.value()-y_offset)*50/scale)+250)
					except:
						domain_issues = True
						oldCoords = None
						continue


					check_x = max(-1000, min(1500, check_x))
					check_y = max(-1000, min(1500, check_y))

					try: diff = abs(check_y - oldCoords[1])
					except: diff = 0

					if diff > 2000:
						oldCoords = None

					graph.paste(pixel,(check_x-1, check_y-1))

					if oldCoords != None:
						draw.rectangle([(check_x+1, check_y),oldCoords],fill=colors[func_num])

					oldCoords = (check_x-1, check_y)

		funcnames = funcnames.replace(' **, **', '')
		if len(functions) == 2: funcnames = funcnames.replace(", ", " ")
		addendum = ''
		if scale != 2: addendum += f"\nScale: **{scale/2}**"
		if x_offset != 0: addendum += f"\nX offset: **{x_offset}**"
		if y_offset != 0: addendum += f"\nY offset: **{y_offset}**"

		path = f'Helper/books/{command_user(ctx).id}.png'
		graph.save(path,"PNG")

		e = dc.Embed(title = "Graphing...",description=f"Graph of **{funcnames}**{addendum}")
		e.set_image(url=f"attachment://{command_user(ctx).id}.png")
		e.set_footer(text=f"Each {'thick ' if hasThin else ''}gray line is {'10^'+str(int(math.log10(magnitude))) if abs(math.log10(magnitude)) > 10 else (int(magnitude) if magnitude >= 1 else magnitude)} unit{'s' if magnitude != 1 else ''}.")

		await ctx.reply(embed=e,file=discord.File(path))
		os.remove(path)
		return



	async def desmos_experimental(self, ctx, functions, scale="1.0", x_offset="0.0", y_offset="0.0"):
		functions = parse_funcs(functions)[:3]
		error = 0.04
		try:
			x_offset = float(x_offset)
			y_offset = float(y_offset)
			scale = float(scale)
			error = float(error)
		except:
			raise cmd.errors.ArgumentParsingError()

		addendum = ''
		if scale != 2: addendum += f"\n(Warning: scaling graphs with this argument may have strange effects)\nScale: **{scale/2} **"
		if x_offset != 0: addendum += f"\nX offset: **{x_offset}**"
		if y_offset != 0: addendum += f"\nY offset: **{y_offset}**"




		colors = [
			"#dd4444", "#44dd44", "#4444dd", "#44dddd", "#dd44dd", "#dddd44", "#dddddd", "#444444"
		]

		st = cexprtk.Symbol_Table(variables={
			"x": 0,
			"y": 0,
			"e": math.e,
			'phi':(1+5**0.5)/2
		},
															add_constants=True,
															functions=self.added_funcs)

		graphsize = int(math.floor(((400**2)/(len(functions)**0.7))**0.5))
		graph = Image.new("RGBA", (graphsize, graphsize), (0, 0, 0, 0))
		draw = ImageDraw.Draw(graph)


		magnitude = 10**(math.ceil(math.log10(scale/(2))))
		movement = (graphsize*magnitude)/(scale*10)

		thickColor = '#80808040'

		startPos = ((-(graphsize/2)*(10*scale/graphsize)+x_offset)//magnitude*magnitude-x_offset)*graphsize/(scale*10)+graphsize/2
		while startPos <= graphsize:
			draw.rectangle([(round(startPos)-1,0),(round(startPos),graphsize-1)],fill=thickColor)
			startPos += movement

		startPos = (graphsize-1)-((math.ceil(((graphsize/2)*(10*scale/graphsize)+y_offset)/magnitude)*magnitude-y_offset)*graphsize/(scale*10)+graphsize/2)
		while startPos <= graphsize:
			draw.rectangle([(0,round(startPos)-1),(graphsize-1,round(startPos))],fill=thickColor)
			startPos += movement


		draw.rectangle(
			[(math.ceil(.49 * graphsize) - int(x_offset *
																				 (graphsize * 0.1) / scale), 0),
			 (math.floor(.51 * graphsize) - int(x_offset * (graphsize * 0.1) / scale),
				graphsize - 1)],
			fill="#ffffff")
		draw.rectangle(
			[(0, math.ceil(.49 * graphsize) + int(y_offset *
																						(graphsize * 0.1) / scale)),
			 (graphsize - 1, math.floor(.51 * graphsize) +
				int(y_offset * (graphsize * 0.1) / scale))],
			fill="#ffffff")

		funcnames = ' '

		for func_num in range(len(functions)):
			function = functions[func_num]
			comprtype = '='
			for comprtypet in [">=", "<=", "<", ">", "=", '=='][::-1]:
				exprs = function.split(comprtypet)[:2]
				if len(exprs) == 2:
					comprtype = comprtypet
					break

			funcnames += ("**, and** `" if func_num == len(functions)-1 and len(functions) != 1 else "**, **`")+function+'`'

			if len(exprs) == 1: exprs += ['y']

			try: calcs = [cexprtk.Expression(exprs[0], st), cexprtk.Expression(exprs[1], st)]
			except: 
				await ctx.respond("There was an error parsing your input. Here's some possible reasons:\n- You forgot a parenthesis somewhere\n- You used an invalid variable (like xy when you mean x*y)\n- You tried to use unsupported syntax (like x! for factorial) or function (see https://pastebin.com/ev79QPxC)")
				return		

			pixel = Image.new("RGBA", (3, 3), colors[func_num])
			for check_x in range(graphsize):


				for check_y in range(graphsize):
					global num
					num = check_x % 2
					in_x = 10 * (check_x - graphsize / 2) * (scale / graphsize) + x_offset
					in_y = -10 * (check_y - graphsize / 2) * (scale / graphsize) + y_offset
					st.variables['x'] = in_x
					st.variables['y'] = in_y
					try:
						e1 = calcs[0].value()
						e2 = calcs[1].value()
					except cexprtk.ParseException:
						return

					compare = False
					if comprtype == '=': compare = abs(e1 - e2) < scale**1 * error
					if comprtype == '>': compare = e1 > e2
					if comprtype == '<': compare = e1 < e2
					if comprtype == '>=': compare = e1 >= e2
					if comprtype == '<=': compare = e1 <= e2

					if compare:
						graph.paste(pixel, (check_x - 1, check_y - 1))

					units = 10**math.floor(math.log10(scale))


		funcnames = funcnames.replace(' **, **', '')
		if len(functions) == 2: funcnames = funcnames.replace(", ", " ")

		path = f'Helper/books/{command_user(ctx).id}.png'
		graph = graph.resize((graphsize*2,graphsize*2), resample=Image.BOX)
		graph.save(path,"PNG")
		embed = dc.Embed(title = "Experimental Graphing...",description=f"Graph of **{funcnames}**{addendum}")
		embed.set_image(url=f"attachment://{command_user(ctx).id}.png")
		embed.set_footer(text=f"Each gray line is {'10^'+str(int(math.log10(magnitude))) if abs(math.log10(magnitude)) > 10 else (int(magnitude) if magnitude >= 1 else magnitude)} unit{'s' if magnitude != 1 else ''}.")

		await ctx.respond(embed=embed,file=discord.File(path))
		os.remove(path)
		return





