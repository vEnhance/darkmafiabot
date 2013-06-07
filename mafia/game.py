import copy
import types
import random

import lib
import roles
import player

class FakeMaster():
	def mkRequest(self, name, *args, **kwargs):
		print lib.colors.STARTCOLOR, name, lib.colors.ENDCOLOR + ":", args, kwargs
	def setPhaseTimer(self, *args, **kwargs):
		print lib.colors.STARTCOLOR, "Timer", lib.colors.ENDCOLOR + ":",  args, kwargs

class MafiaGame():	
	""" MafiaGame instance.
	This is controlled by the GameUnit model."""

	master = None
	game_name = ""

	#Initialize Mafia Game {{{1
	def __init__(self, setup, **kwargs):
		#Game vars
		self.game_started = 0
		self.game_over = 0
		
		#Bot vars
		self.team_count = {}
		
		#Setup vars
		self.setup = copy.copy(setup)
		self.player_list = copy.copy(setup)
		if kwargs.get("shuffle", True):
			random.shuffle(self.player_list)
		self.num_alive = len(setup)
		
		#Daily vars
		self.daylight = 1  #phase flag - currently day (night is 0)
		self.day = 0 # day 0		
		self.the_no_lynch = player.NoLynch() # patch vote glitch
		self.day_max_len = 300 # seconds
		self.night_max_len = 25
		
		#Nightly vars
		self.nightless = 0
		self.has_night = []
		self.waiting_night = []
		
		self.peaceful_night = 1
		self.night_queue = {0:{}}
		
		# Deal with players
		for n in range(0, len(self.player_list)):
			currPlayer = self.player_list[n]
			currPlayer.parent_game = self
			currPlayer.pid = n
			if currPlayer.public_name is None:
				currPlayer.public_name = "SLOT" + str(n)
			if currPlayer.private_name is None:
				currPlayer.private_name = "Player " + str(n)
			self.team_count[currPlayer.align] = self.team_count.get(currPlayer.align, 0) + 1
			if currPlayer.has_night:
				self.has_night.append(currPlayer)

		for key in kwargs:
			setattr(self, key, kwargs[key])
	
	# __repr__ and __getitem__, for debugging use mainly {{{1
	def __repr__(self):
		return self.game_name

	def __getitem__(self, i):
		return self.player_list[i]
	
	#Change phase functions {{{1
	def startDay(self):
		if self.game_over: return
		self.resolveNight()
		if self.game_over: return
	
		self.resetDayNight()
		
		#Advance Day
		self.day += 1
		self.daylight = 1
		
		#Check to see if game should end
		if self.day >= len(self.setup)*2.718281828459:
			self.master.mkRequest(name = "long_end") # Tell master that a long game ended
			self.runGameOver()
			return

		# New timer
		self.master.setPhaseTimer(self.day_max_len)
		# Tell master to tell other people about a new day
		self.master.mkRequest(name = "new_day")

		
	def startNight(self):
		if self.checkIfWin(): return
		if self.nightless == 1:
			self.endNight()
			return
		if self.checkIfWin(): return
		
		#Reset nightly vars
		self.resetDayNight()
		self.daylight = 0

		# New timer
		self.master.setPhaseTimer(self.night_max_len)
		# Tell master to prepare for a new night
		self.master.mkRequest(name = "new_night")

	#Alias peoples
	endDay = startNight
	endNight = startDay

	def endPhase(self):
		if self.game_over == 1: return
		if self.daylight:
			self.endDay()
		else:
			self.endNight()

	#Gamestart function
	def startGame(self, phase=1):
		self.master.mkRequest(name = "game_start")
		self.game_started = 1
		if phase==1: self.startDay()
		else: self.startNight()
	
	def killPlayer(self, target, reason="Unknown Reason", surpress = 0): # kills a player in the game {{{1
		if target.alive == 0:
			return # already dead, wtf?
		target.death_reason = reason
		target.alive = 0

		# Change counts
		self.num_alive -= 1
		self.team_count[target.align] -= 1

		# Run onDeath
		target.onDeath()

		# Tell master that someone died
		self.master.mkRequest(name="death", player=target)

		if surpress == 0:
			self.checkIfWin()
	 
	# Check if win; run game over {{{1
	def checkIfWin(self):
		#Check if win.  Additionally, returns self.game_over
		currentTeams = copy.copy(self.team_count)
		currentTeams[-2] = 0
		checkWinKeys = copy.copy(currentTeams.values())
		checkWinKeys.sort()
		if checkWinKeys[0:-1] == [0]*(len(checkWinKeys)-1) and self.team_count.get(-1,0) < 2:
			self.runGameOver()
		return self.game_over

	def runGameOver(self):
		if not self.game_over: self.master.mkRequest(name="game_over")
		self.game_over = 1
	
	# Misc {{{1
	def pubLog(self, text):
		self.master.mkRequest(name="public_log", text=text)

	def p(self, req):
		# Converts a request to a player
		if type(req) == types.IntType:
			return self.player_list[req]
		elif type(req) == types.StringType:
			if str.isdigit(req):
				return self.player_list[int(req)]
			for player in self.player_list:
				if player.public_name == req: return player
			return None
		elif type(req) == types.UnicodeType:
			for player in self.player_list:
				if player.public_name == req: return player
			return None
		elif isinstance(req, roles.Player):
			return req
		else:
			return None
	
	def inProgress(self):
		return self.game_started and not self.game_over
	 
	#Day and night related functions {{{1
	#=============================================================================
	#Resolving Night actions
	
		# DEVELOPING NIGHT QUEUES: DOCUMENTATION:
		# values are
		# action= {function}
		# user = {MafiaPlayer instance}
		# args = arguments for main function
		
	def submitNightAction(self, key, priority, **valueDict):
		# key should be distinct, used to prevent people from submitting multiple night actions
		self.night_queue[self.day] = self.night_queue.get(self.day, {})
		self.night_queue[self.day][key] = (priority, valueDict)
		#Low numbers => higher priority
		
	
	def resolveNight(self):
		# Run through the queue and do actions
		if self.night_queue != {0:{}}:
			sortedQueue = self.night_queue.get(self.day, {}).values()
			sortedQueue.sort() #This causes a sort by priority
			for currList in sortedQueue:
				action_dict = currList[1]
				queue_args = action_dict["args"]
				queue_caster = action_dict["caster"]
				queue_function = action_dict["action"]
				queue_action_name = action_dict["action_name"]
				if queue_caster.roleblocked == "NO":
					queue_function(*queue_args)
				for target in queue_args[1:]:
					if target.paranoid == "YES":
						target.addDeathMark(by=queue_caster, day=self.day)
				if queue_caster.num_left[queue_action_name] != -1:
					queue_caster.num_left[queue_action_name] -= 1
		#Proceed to kill if necessary		

		for victim in self.player_list:
			if not victim.alive: continue
			if not victim.death_marks.has_key(self.day): continue
			if victim.bulletproof == "SINGLE":
				victim.bulletproof = "NO"
			elif victim.bulletproof == "NO":
				self.killPlayer(victim, "Killed Night %d" %self.day, surpress = 1)
				who_fault = victim.death_marks[self.day]
				victim.onNightKill(who_fault)
			else:
				pass
		
		self.checkIfWin()		
		

	def resetDayNight(self):
		for currPlayer in self.player_list+ [self.the_no_lynch]:
			#Reset any bulletproof or roleblocked statuses
			if self.daylight==0:
				if currPlayer.bulletproof == "TONIGHT": currPlayer.bulletproof = "NO"
				if currPlayer.roleblocked == "TONIGHT": currPlayer.roleblocked = "NO"
			else:
				if currPlayer.unlynchable == "TODAY": currPlayer.unlynchable = "NO"
			
				#Reset all votes
				currPlayer.vote_target = None
		
		#Game-level vars
		self.peaceful_night = 1 #Flag
	
	def getCurrentPhase(self):
		return "Day %d" %self.day if self.daylight else "Night %d" %self.day

	# }}}

# vim: foldmethod=marker
