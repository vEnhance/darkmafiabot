import mafia.setups
import string
import lib

class Lobby:
	LOBBY_COMMANDS = ('confirm', 'setup', 'setup_', 'start', 'register')

	def __init__(self, master):
		self.master = master
		self.signed_up = []

	def handle(self, **kwargs):
		return getattr(self, "handle_" + kwargs['cmd_name'])(**kwargs)

	def handle_confirm(self, **kwargs):
		new_name = kwargs['request'] # If there is a name afterwards in the confirm
		new_address = kwargs['address'] # e.g. bob@mit.edu
		if new_name.strip() == "":
			new_name = lib.DEFAULT_PUBLIC_NAMES.get(kwargs['sender'], kwargs['sender']) # e.g. kwargs['sender'] = "chen.evan6"

		# Make sure user isn't already registered
		for spot in self.master.game.player_list:
			if spot.gmail_username == new_address:
				return "You have already registered for this Mafia game."
			if spot.public_name == new_name:
				return "The name %s is already taken." %new_name

		# Search for unused spots
		for spot in self.master.game.player_list:
			# Determine whether the spot is open
			if not spot.activated:
				spot.public_name = new_name
				spot.gmail_username = new_address
				spot.activated = True
				self.master.mkRequest('public_log', text = "%s has joined the game." %new_name)
				return 0
		else:
			return "The game you are trying to register for is full."
	handle_register = handle_confirm
	
	def handle_start(self, **kwargs):
		if not self.master.game.game_started:
			self.master.game.startGame()
			return 0
		else:
			return "/start has no effect; the game has already started"
	
	# This is "setup!".  Bangs get converted to _ in controller.
	def handle_setup_(self, **kwargs):
		data = kwargs['request'].strip().split(' ')
		setup_name = "setup_" + data[0].lower()
		args = data[1:]
		if any([char not in string.lowercase + string.digits +"_" for char in setup_name]): # guard against screwy users
			return "Setup names are alphanumeric.  No such setup %s." %(data[0].lower())
		if not hasattr(mafia.setups, setup_name):
			return "No such setup!"
		setup_constructor = getattr(mafia.setups, setup_name)
		try:
			game_instance = setup_constructor(*args)
			self.master.registerGame(game_instance)
			self.master.mkRequest("new_game")
			return "Setup done."
		except TypeError as e:
			return  e[0] + "\n" + "TypeError; here is argument documentation:\n" + setup_constructor.__doc__
		except AssertionError as e:
			return e[0]
		except Exception as e:
			return e[0]
	def handle_setup(self, **kwargs):
		if not self.master.game.game_over:
			return "Game %s has not ended.  Use /setup! to kill that game." %(self.master.game)
		else:
			return self.handle_setup_(**kwargs)
