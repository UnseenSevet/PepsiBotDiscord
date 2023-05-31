from Helper.__functions import is_whole
from Helper.__bpp_functions import express_array, safe_cut, FUNCTIONS
#from Helper.__db import Database
from PIL import Image, ImageDraw, ImagePath, ImageOps
import json, os
from Helper.__comp import *

def add_tag(args):
	with open("DB/bpp_programs.json","r") as f:
		data = json.load(f)
	data[args[0]] = args[1:]
	with open("DB/bpp_programs.json","w") as f:
		f.write(json.dumps(data,indent="\t"))
	return

def remove_tag(name):
	with open("DB/bpp_programs.json","r") as f:
		data = json.load(f)
	del data[name]
	with open("DB/bpp_programs.json","w") as f:
		f.write(json.dumps(data,indent="\t"))
	return

def edit_tag(name, program=None, uses=None, lastUsed=None):
	with open("DB/bpp_programs.json","r") as f:
		data = json.load(f)

	edited = data[name]
	if program != None:
		edited[0] = program
	if uses != None:
		edited[2] = uses
	if lastUsed != None:
		edited[4] = lastUsed

	data[name] = edited
	with open("DB/bpp_programs.json","w") as f:
		f.write(json.dumps(data,indent="\t"))
	return

def get_tags(program=False, author=False, uses=False, created=False, lastUsed=False):
	with open("DB/bpp_programs.json","r") as f:
		data = json.load(f)
	out = []
	for x in data.keys():
		append = [x]
		if program: append += [data[x][0]]
		if author: append += [data[x][1]]
		if uses: append += [data[x][2]]
		if created: append += [data[x][3]]
		if lastUsed: append += [data[x][4]]
		out += [append]
	return out


def get_globals(name=False,vtype=False,owner=False):
	with open("DB/bpp_globals.txt","r") as f:
		gvars = [x.strip().split(",") for x in f.readlines()]
	gvars = [x for x in gvars if x != ['']]

	out = []
	for x in gvars:
		add = []
		if name: add.append(x[0])
		if vtype: add.append(x[1])
		if owner: add.append(x[2])
		out.append(add)
	return out

def get_global(name):
	gvars = get_globals(name=True,vtype=True)
	with open("DB/bpp_globals/"+name+".txt","r") as f:
		value = f.read()
	out = [[x[0],value,x[1]] for x in gvars if x[0] == name][0]
	return out

def add_global(values):
	with open("DB/bpp_globals.txt","a") as f:
		f.write(",".join([str(x) for x in [values[0],values[2],values[3]]]))
		f.write("\n")
	with open("DB/bpp_globals/"+values[0]+".txt","w") as f:
		f.write(values[1])

def edit_global(name,value,vtype):
	gvars = get_globals(name=True,vtype=True,owner=True)

	for x in range(len(gvars)):
		if gvars[x][0] == name:
			loc = x
			vardata = gvars[x]
			break

	gvars[loc] = [vardata[0],vtype,vardata[2]]
	with open("DB/bpp_globals.txt","w") as f:
		f.writelines([",".join([str(z) for z in x])+"\n" for x in gvars])
	with open("DB/bpp_globals/"+name+".txt","w") as f:
		f.write(value)
	return

def run_bpp_program(code, p_args, author, runner):
	# Pointers for tag and function organization
	tag_level = 0
	tag_code = []
	global tag_images
	tag_images = []
	tag_str = lambda: ' '.join([str(s) for s in tag_code])

	backslashed = False	# Flag for whether to unconditionally escape the next character

	functions = {}	# Dict flattening a tree of all functions to be evaluated

	current = ["", False] # Raw text of what's being parsed right now + whether it's a string

	output = "" # Stores the final output of the program

	goto = 0 # Skip characters in evaluating the code

	for ind, char in enumerate(list(code)):
		normal_case = True

		if ind < goto:
			continue

		if backslashed:
			if tag_code == []:
				output += char
			else:
				current[0] += char

			backslashed = False
			continue

		if char == "\\":
			backslashed = True
			continue

		if char == "[" and not current[1]:
			tag_level += 1

			if tag_level == 1:
				try:
					tag_code = [max([int(k) for k in functions if is_whole(k)]) + 1]
				except ValueError:
					tag_code = [0]
				
				output += "{}"

				found_f = ""

				for f_name in FUNCTIONS.keys():
					try:
						attempted_f = ''.join(code[ind+1:ind+len(f_name)+2]).upper()
						if attempted_f == f_name + " ":
							found_f = f_name
							goto = ind + len(f_name) + 2
						elif attempted_f == f_name + "]":
							found_f = f_name
							goto = ind + len(f_name) + 1
					except IndexError: pass
				
				if found_f == "":
					end_of_f = min(code.find(" ", ind+1), code.find("]", ind+1))
					called_f = ''.join(code[ind+1:end_of_f])
					raise NameError(f"Function {called_f} does not exist")
				
				functions[tag_str()] = [found_f]
			
			else:
				old_tag_code = tag_str()
				
				k = 1
				while old_tag_code + f" {k}" in functions.keys():
					k += 1

				new_tag_code = old_tag_code + f" {k}"

				found_f = ""

				for f_name in FUNCTIONS.keys():
					try:
						attempted_f = ''.join(code[ind+1:ind+len(f_name)+2]).upper()
						if attempted_f == f_name + " ":
							found_f = f_name
							goto = ind + len(f_name) + 2
						elif attempted_f == f_name + "]":
							found_f = f_name
							goto = ind + len(f_name) + 1
					except IndexError: pass
				
				if found_f == "":
					end_of_f = min(code.find(" ", ind+1), code.find("]", ind+1))
					called_f = ''.join(code[ind+1:end_of_f])
					raise NameError(f"Function {called_f} does not exist")

				functions[new_tag_code] = [found_f]
				functions[tag_str()].append((new_tag_code,))

				tag_code.append(k)
			
			normal_case = False
		
		if char == "]" and not current[1]:
			if current[0] != "":
				functions[tag_str()].append(current[0])
				current = ["", False]
			tag_level -= 1
			normal_case = False
		
		if char == " ":
			if not current[1] and tag_level != 0:
				if current[0] != "":
					functions[tag_str()].append(current[0])
					current = ["", False]
				normal_case = False
		
		if char in '"“”':
			if current[0] == "" and not current[1]:
				current[1] = True
			elif current[1]:
				functions[tag_str()].append(current[0])
				current = ["", False]
			normal_case = False
		
		if normal_case:
			if tag_level == 0: output += char
			else: current[0] += char
		
		tag_code = tag_code[:tag_level]
		tag_code += [1] * (tag_level - len(tag_code))

	VARIABLES = {}

	base_keys = [k for k in functions if is_whole(k)]

	type_list = [int, float, str, list, Image.Image]
	def var_type(v):
		try:
			return type_list.index(type(v))
		except IndexError:
			raise TypeError(f"Value {safe_cut(v)} could not be attributed to any valid data type")
	
	def evaluate_result(k):
		global tag_images
		v = functions[k]

		if type(v) == tuple:
			k1 = v[0]
			functions[k] = evaluate_result(k1)
			return functions[k]
		
		args = v[1:]

		for i, a in enumerate(args):
			if v[0] == "IF" and is_whole(v[1]) and int(v[1]) != 2-i:
				continue
			if type(a) == tuple:
				k1 = a[0]
				functions[k][i+1] = evaluate_result(k1)
		
		args = v[1:]

		result = FUNCTIONS[v[0]](*args)

		# Tuples indicate special behavior necessary
		if type(result) == tuple:
			if result[0] == "d":
				if len(str(result[1])) > 100000:
					raise MemoryError(
					f"The variable {safe_cut(args[0])} is too large: {safe_cut(result[1])} (limit 100kb)")
					
				VARIABLES[args[0]] = result[1]
				result = ""

			elif result[0] == "v":
				try:
					result = VARIABLES[args[0]]
				except KeyError:
					raise NameError(f"No variable by the name {safe_cut(args[0])} defined")

			elif result[0] == "a":
				if result[1] >= len(p_args) or -result[1] >= len(p_args) + 1:
					result = ""
				else:
					result = p_args[result[1]]

			elif result[0] == "gd":
				v_name = args[0]
				if len(str(result[1])) > 100000:
					raise MemoryError(
					f"The global variable {safe_cut(v_name)} is too large: {safe_cut(result[1])} (limit 100kb)")
				
				if [v_name] not in get_globals(name=True):
					v_value = express_array(result[1]) if type(result[1]) == list else result[1]

					add_global([v_name, str(v_value), var_type(v_value), str(author)])
					result = ""

				else:
					v_list = get_globals(name=True,owner=True)
					v_owner = [v for v in v_list if v_name == v[0]][0][1]

					if v_owner != str(author):
						raise PermissionError(
						f"Only the author of the {v_name} variable can edit its value ({v_owner})")
					
					edit_global(name=v_name, value=str(result[1]), vtype=var_type(result[1]))
					result = ""
				
			elif result[0] == "gv":
				v_name = args[0]

				if [v_name] not in get_globals(name=True):
					raise NameError(f"No global variable by the name {safe_cut(v_name)} defined",get_globals(name=True))

				v_list = get_global(v_name)
				v_value, v_type = v_list[1:3]
				v_value = type_list[int(v_type)](v_value)

				result = v_value

			elif result[0] == "n":
				result = runner.name

			elif result[0] == "id":
				result = runner.id

			elif result[0] == "gid":
				try: result = runner.guild.id
				except: result = 0

			elif result[0] == "aa":
				result = p_args
		
			elif result[0] == 'atc':
				if len(tag_images) >= 2:
					raise ValueError("Cannot attach more than two images to the program output!")
				im = result[1]
				path = f'Helper/Assets/{runner.id}_tagimg_{len(tag_images)}.png'
				im.save(path,"PNG")
				tag_images += [dc.File(path)]
				os.remove(path)
				result = ""
		
		functions[k] = result
		return result

	for k in base_keys:
		evaluate_result(k)
	
	for k in base_keys:
		if type(functions[k]) == tuple:
			evaluate_result(k)

	results = []
	for k, v in functions.items():
		if is_whole(k):
			if type(v) == list: v = express_array(v)
			results.append(v)

	output = output.replace("{}", "\t").replace("{", "{{").replace("}", "}}").replace("\t", "{}")

	return (output.format(*results).replace("\v", "{}"),tag_images)

if __name__ == "__main__":
	program = input("Program:\n\t")
	print("\n")
	program = program.replace("{}", "\v")
	print(run_bpp_program(program, [], 184768535107469314))
