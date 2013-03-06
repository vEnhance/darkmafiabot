import random
from time import ctime
import time

import lib

class Viewer:
	VIEW_COMMANDS = ['view', 'get', 'help', 'status'] 

	def __init__(self, master):
		self.master = master

	def deathStatus(self, player):
		if not player.lying_role or player.parent_game.game_over:
			return "[%s] %s, %s.  %s." %(player, player.private_name, player.player_type, player.death_reason)
		else:
			return "[%s] %s, %s.  %s." %(player, player.private_name, player.alt_player_type, player.death_reason)

	def handle(self, **kwargs):
		return getattr(self, "handle_" + kwargs['cmd_name'])(**kwargs)

	# Handlers (for commands) {{{1
	def handle_status(self, **kwargs):
		mgcurr = self.master.game
		header = "The game %s" % mgcurr
		if mgcurr.game_over == 1:
			header += " has ended."
		elif mgcurr.game_started == 0:
			header += " has not yet started."
		else:
			header += " is in " + ("Day" if mgcurr.daylight == 1 else "Night") + " " + str(mgcurr.day) + "."
		alive_printout = "===== ALIVE ====="
		dead_printout =  "===== DEAD ====="
		
		for curr_player in mgcurr.player_list:
			if curr_player.alive == 1:
				alive_printout += "\n" + ("%d. %s (%d): %s \n....Currently voting %s" \
						%(curr_player.pid, curr_player, len(curr_player.voters),
						[mgcurr.p(voter_pid).public_name for voter_pid in curr_player.voters], curr_player.vote_target))
			else:
				dead_printout += "\n" + ("%d. %s" %(curr_player.pid, self.deathStatus(curr_player)))
		return header + "\n" + alive_printout + "\n \n" + dead_printout

	def handle_view(self, **kwargs):
		request = kwargs['request']
		if request == 'status': 
			return self.handle_status(**kwargs)
		elif request == 'pm':
			if not self.master.game.game_started:
				return "You may not view your role PM until the game starts."
			elif kwargs['is_group']:
				return "Please use a private channel when viewing your role PM."
			else:
				caster = kwargs['caster']
				ret = "ROLE PM for game %s" %self.master.game
				ret += "\n"
				ret += "="*16
				ret += "\n"
				ret += "You are a %s.  People know you as %s." %(caster.player_type, caster.private_name)
				ret += "\n"
				ret += caster.rolePM
				return ret
		elif request == 'time':
			return self.handle_time(**kwargs)
		return request
	handle_get = handle_view

	def handle_help(self, **kwargs):
		return lib.HELP_MSG

	def handle_time(self, **kwargs):
		return "Current phase ends in %f seconds." %(self.master.next_time - time.time())

	def handle_roll(self, **kwargs):
		n = int(kwargs['request'])
		return "The roll resulted in %d." %(random.randrange(0,n)+1)
	
	# Updaters (when model says so) {{{1

	def pubLog(self, text):
		self.master.send_message(mto=self.master.room, mbody=text, mtype='groupchat')
		return 0
	def quietLog(self, to, text):
		if to.activated:
			self.master.send_message(mto=to.public_name + "@gmail.com", mbody=text, mtype='chat')
		return 0
	update_public_log = pubLog
	update_quiet_log = quietLog

	def update(self, name, **kwargs):
		cmd = "update_" + name
		if hasattr(self, cmd):
			return getattr(self, cmd)(**kwargs)
		else:
			return "No method %s exists." %(cmd)
	# }}}

	# Phase {{{2
	def update_new_game(self):
		self.master.sendPresence("chat", "The new game \"%s\" has opened!" %(self.master.game))

	def update_long_end(self):
		self.pubLog("Maximum game length exceeded.  Everyone lives happily ever after.")

	def update_new_day(self):
		mgcurr = self.master.game
		end_time = self.master.next_time - time.time()
		self.master.sendPresence("available", "Day %d, %s" %(mgcurr.day, mgcurr))
		self.pubLog("*" * 12 + "\nDay %d ends in at most %d seconds at %s.\
				\nWith %d alive, it takes %d to lynch." \
				%(mgcurr.day, mgcurr.day_max_len,
				ctime(end_time)[-13:-5], mgcurr.num_alive, int(mgcurr.num_alive/2 + 1)))

	def update_new_night(self):
		mgcurr = self.master.game
		end_time = self.master.next_time - time.time()
		self.master.sendPresence("busy", "Night %d, %s" %(mgcurr.day, mgcurr))
		# TODO Set status
		self.pubLog("*" * 12 + "\nNight %d ends in at most %d seconds at %s." %(mgcurr.day, mgcurr.night_max_len, ctime(end_time)[-13:-5]))

	# Death & game start/over {{{2
	def update_death(self, player):
		args = [1] if player.public_name in lib.FEMALE_PLAYERS else []
		self.pubLog(lib.haiku.haikuGet(*args) + "\n%s is now dead.  RIP!\n" %player + self.deathStatus(player) + "\n")
	
	def update_game_start(self):
		self.pubLog("*** GAME %s HAS STARTED ***" %self.master.game)
		for player in self.master.game.player_list:
			player.quietLog(player.rolePM)
	
	def update_game_over(self):
		res = "****GAME OVER****"
		for curr_player in self.master.game.player_list:
			player_info = self.deathStatus(curr_player)
			res += "\n" + player_info
		res += "\nGame %s has ended." %self.master.game
		self.master.sendPresence("chat", "Game %s has ended." %self.master.game)
		self.pubLog(res)

	# Votes, lynches, ... {{{3
	def update_vote_change(self, caster, target, apparent_lynch_count):
		if apparent_lynch_count >= 0: 
			toPubLog = "%s: *VOTE: %s*.  L-%d." %(caster, target, apparent_lynch_count)
		else:
			toPubLog = "%s: *VOTE: %s*.  L+%d." %(caster, target, -apparent_lynch_count)
		self.pubLog(toPubLog)
	def update_unvote(self, caster):
		self.pubLog("%s: *UNVOTE*" %caster)
	def update_lynch_success(self, target):
		self.pubLog("*** LYNCH ***")
	def update_lynch_failure(self, target):
		self.pubLog("A lynch failed to take place...")
	def update_lynch_nolynch(self, target):
		self.pubLog("*** NO LYNCH ***")

	# Misc Notifications {{{3
	def update_action_not_allowed(self, caster):
		self.quietLog(to=caster, text="Invalid command.")
	def update_command_received(self, caster):
		self.quietLog(to=caster, text="Your command has been successfully queued.")
	# }}}
	# }}}


#vim: foldmethod=marker
