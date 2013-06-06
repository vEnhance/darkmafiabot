import copy
import voting
import allies

# Player class

DEFAULT_DAY = {
		'vote' : voting.action_vote,
		'unvote' : voting.action_unvote,
		'votenolynch' : voting.action_votenolynch
		}
DEFAULT_NIGHT = {
		'nighttalk': allies.action_night_talk,
		'allies' : allies.action_allies,
		'changechannel' : allies.action_change_channel,
		'channels' : allies.action_view_channels,
		}


class Player():
	#Logistics
	parent_game = None
	alive = 1 # 0 when not alive
	align = None # alignment
	vote_target = None # keeps track of who's voting what
	
	num_votes_on = 0 # sum of weights of people voting me
	bah = 0
	
	#mods
	lying_role = 0 # Added by james4l. Used for millers and cops that die differently
	# if lying_role = 1, on death, player.alt_player_type will be shown instead of player_type
	death_reason = "Alive"
	
	bulletproof = "NO" #other settings will be SINGLE, TONIGHT and ALL
	roleblocked = "NO" #other settings will be TONIGHT and ALL
	unlynchable = "NO" #settings will be TODAY and ALL
	paranoid = "NO" # settings will be YES and NO (paranoid gun owner)
	vote_weight = 1 # weight of a vote (e.g. doublevoter = 2)
	
	#More logistics
	has_night = True
	can_night_talk_public = False
	
	player_type = "ERRORPERSON"
	rolePM = "You are bored."
	
	# Methods
	day_methods = DEFAULT_DAY
	night_methods = DEFAULT_NIGHT

	#Names
	public_name = None
	private_name = None
	pid = None

	activated = False
	
	# Talk Channel System {{{1
	talk_index = 0 # The currently addressed channel
	talk_channels = [] # List of acceptable talk channels
	def currentChannel(self):
		return self.talk_channels[self.talk_index] if len(self.talk_channels) >= 1 else None
	def getAllies(self):
		curr_channel = self.currentChannel()
		if curr_channel == None: return []
		return [player for player in self.parent_game.player_list if curr_channel in player.talk_channels and player.alive]
	# }}}
	
	def __init__(self, private_name = None, **kwargs):
		# Initialize method dictionaries
		self.day_methods = copy.copy(self.day_methods)
		self.night_methods = copy.copy(self.night_methods)
		self.num_left = {}
		# Place limited uses on any methods with a maximum use limit
		for method_dict in (self.day_methods, self.night_methods):
			for method_name in method_dict:
				method = method_dict[method_name]
				self.num_left[method_name] = method.max_uses
		self.endow()

		# Set non-primitive attributes:
		self.death_marks = {} # death marks
		# key is night number, value is killer
		self.voters = [] # list of people voting me

		for key in kwargs:
			setattr(self, key, kwargs[key])
		if private_name is not None:
			self.private_name = private_name
	def __repr__(self):
		return self.public_name

	def endow(self):
		"""Called at the beginning of __init__."""
		pass

	def act(self, act_name, request):
		"""Causes the character to perform act_name with certain arguments (specified as request)."""
		if not self.parent_game.inProgress():
			self.quietLog("Not allowed to perform actions when game is not in progress")
			return
		# Performs an act based on a name
		action_obj = self.getMethod(act_name)
		if action_obj is None:
			self.parent_game.master.mkRequest(name = "action_not_allowed", caster = self)
			return 1 # returns 1 so core knows a bad action occurred, maybe.
		# Create an instance of that action class
		action_obj(caster = self, name = act_name, request = request)
		return 0

	def getMethod(self, name): 
		# get a method by name from current phase list
		# returns None on failure
		methods = self.day_methods if self.parent_game.daylight == 1 else self.night_methods
		return methods.get(name, None)
	
	#Special events
	def onLynch(self, caster): pass
	def onNightKill(self, caster): pass
	def onDeath(self): pass

	def quietLog(self, text):
		# Relay to master
		self.parent_game.master.mkRequest(name = "quiet_log", text = text, to = self)
	
	def addDeathMark(self, by, day):
		# Marks a death day for a player
		if not self.death_marks.has_key(day):
			self.death_marks[day] = by

#Dummy player for NoLynch
class NoLynch(Player):
	align = 0
	player_type = "NOLYNCH"
	rolePM= "NO U"
	def __init__(self, *args):
		self.public_name = "NOLYNCH"
		self.private_name = "NOLYNCH"

# }}}

# vim: fdm=marker
