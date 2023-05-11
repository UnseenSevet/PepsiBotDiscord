from Helper.__comp import *
from random import randint, choice
from time import time
import discord as dc
import re
from copy import deepcopy
from Helper.__config import STARTUP
from Helper.__functions import m_line, command_user
from Helper.__server_functions import member_check

def setup(BOT):
	BOT.add_cog(_8ball(BOT))

class _8ball(cmd.Cog):
	'''
	Ask the 8ball a question and it will bestow its wisdom upon you.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "(query)"
	CATEGORY = "FUN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['ask','8ball',"8"]

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to incompatibility
	@cmd.slash_command(name="8ball")
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def slash_8ball(self, ctx, query=''):
		'''
		Ask the 8ball a question and it will bestow its wisdom upon you.
		'''
		await ctx.response.defer()
		await self._8ball(ctx, query=query)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1, cmd.BucketType.user)
	@cmd.check(member_check)
	async def _8ball(self, ctx, *, query=""):
		args = query
		commands = [
			k.lower() for k, v in self.BRAIN.cogs.items() 
			if "ALIASES" in dir(self.BRAIN.get_cog(k))
		]

		shows = ["Game of Thrones", "Stranger Things", "The Walking Dead", "13 Reasons Why", "The 100", "Orange Is the New Black", "Riverdale", 
		"Grey's Anatomy", "The Flash", "Arrow", "Money Heist", "The Big Bang Theory", "Black Mirror", "Sherlock", "Vikings", "Pretty Little Liars", 
		"The Vampire Diaries", "American Horror Story", "Breaking Bad", "Lucifer", "Supernatural", "Prison Break", "How to Get Away with Murder", "Teen Wolf", 
		"The Simpsons", "Once Upon a Time", "Narcos", "Daredevil", "Friends", "How I Met Your Mother", "Suits", "Mr. Robot", "The Originals", "Supergirl", 
		"Gossip Girl", "Sense8", "Gotham", "Westworld", "Jessica Jones", "Modern Family", "Rick and Morty", "Shadowhunters", "The End of the F***ing World", 
		"House of Cards", "Dark", "Elite", "Sex Education", "Shameless", "New Girl", "Agents of S.H.I.E.L.D.", "You", "Dexter", "Fear the Walking Dead", "Family Guy",
		"The Blacklist", "Lost", "Peaky Blinders", "House", "Quantico", "Orphan Black", "Homeland", "Blindspot", "DC's Legends of Tomorrow", "The Handmaid's Tale",
		"Chilling Adventures of Sabrina", "The Good Doctor", "Jane the Virgin", "Glee", "South Park", "Brooklyn Nine-Nine", "Under the Dome", "The Umbrella Academy",
		"True Detective", "The OA", "Desperate Housewives", "Better Call Saul", "Bates Motel", "The Punisher", "Atypical", "Dynasty", "This Is Us", "The Good Place", 
		"Iron Fist", "The Rain", "Mindhunter", "Revenge", "Luke Cage", "Scandal", "The Defenders", "Big Little Lies", "Insatiable", "The Mentalist", "The Crown",
		"Chernobyl", "iZombie", "Reign", "A Series of Unfortunate Events", "Criminal Minds", "Scream: The TV Series", "The Haunting of Hill House"]

		

		consider = "To find the answer, you should {}.".format(choice(["invest in stocks", "create a bank account", "buy excessive amounts of lotion", "eat a berry",
		"adjust for inflation", "get really into MCSR", "vote", "become rich and successful",
		"breathe more often", "be considerate of your surroundings (except for that guy you want to kill)",
		"become a Doomer", "donate to charity", "hug your mother", "invent a new alphabet", "write",
		"eat ice cream", "forgive yourself", "stop coding this command and go to sleep", "respect people",
		"not start drama all of a sudden", "find love", "copyright your real name",
		"fulfill a technical", "buy a building", "discover how chairs are made", "provide helpful advice",
		"listen to your peers", f"jump off a {randint(1,10)} meter hill", "co-author a paper with Paul Erdős",
		"convert all your data to base e", "play my game", "measure your words", f"draw a {randint(1,361)} degree angle",
		f"turn left then move onward {randint(100,300)} meters before turning right to arrive at your destination",
		"count", "acknowledge the corn", "understand", "drink more water", "drink less water", "buy a tree", "rent a satellite",
		"innovate in the field of electromagnetism", "make a speech about motorbikes", "leave", "appreciate",
		"think about our future", "be responsible", "use this command from time to time", "go to the kitchen",
		"look north", "get ready", "book a flight", "spy on some squirrels", "roll some dice",
		"pick up a sheet of paper and then put it back down again", "draw four", "draw something pretty",
		"do the dishes", "create a new planet", "sleep occasionally", "smile", "come up with a way to recycle linoleum flooring", 
		"open the door", "protest whatever unpopular thing discord is up to"]))

		g = 2017360
		y = 14934838
		r = 13114910
		
		options = [
		("Without a doubt.",g), ("Yes.",g), ("You may rely on it.",g), (consider,y), (consider,y), (consider,y), 
		(f"You should try `p!{choice(commands)}`.",g), (f"Find the answer by watching {choice(shows)}.",y), ("No.",r), ("Very doubtful.",r), ("Outlook bad.",r), ("Reply hazy, try again.",0), ("Better not tell you now.",0)]
		answer = choice(options)
		if re.search("\\bwho\\b", args.lower()) is not None:
			try: user = choice(ctx.guild.members)
			except: user = command_user(ctx)		
			user = f"<@{user.id}>"
			answer = choice([(f"Perhaps {user}.",g), (f"It is {user}.",g), (f"Not {user}.",r)])

		myColor = 0
		e = dc.Embed(title="🎱 The 8ball says...",description=answer[0], color=answer[1])	
		e.set_footer(text=f"Command run by {command_user(ctx).name}")	
		await ctx.respond(embed=e,allowed_mentions = dc.AllowedMentions.none())
		return
			
