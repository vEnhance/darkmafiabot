import random
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
import threading

import sleekxmpp

from mafia import game
import lobby, viewer
import lib

class DarkMafiaBot(sleekxmpp.ClientXMPP): # {{{1
	nick = "darkmafiabot"
	room = "private-chat-05220114-0401-1811-1301-060901021520@groupchat.google.com" 

	# Controller
	CONTROLLER_COMMANDS = ['invite']

	# __init__ and XMPP things {{{1
	def __init__(self, password, jid="darkmafiabot2013@gmail.com", status=None):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.room = "private-chat-%08d-0401-1811-1301-060901021520@groupchat.google.com" %(lib.ROOM_CONVERT.get(jid, random.randrange(10**8)))
		self.initial_status = status

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("message", self.message)
		self.add_event_handler("groupchat_presence", self.muc_presence)

		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0199') # XMPP Ping

		self.game = game.MafiaGame(setup=[
			], game_name="Empty Game") # initial game setup
		self.game.game_over = 1 # Initial game should be already over
		self.game.master = self # sets master to self
		self.lobby = lobby.Lobby(self) # create a lobby manager
		self.viewer = viewer.Viewer(self) # create a viewer

		self.phase_timer = threading.Timer(2**31-1, self.game.runGameOver)
		self.next_time = 2**31 - 1

	def start(self, event):
		self.get_roster()
		self.send_presence()
		# Join the main chat room
		self.plugin['xep_0045'].joinMUC(self.room, self.nick, wait=True)
		if self.initial_status is not None:
			self.sendPresence("chat", self.initial_status)

	def muc_presence(self, presence):
		if presence['muc']['nick'] != self.nick:
			nick = presence['muc']['nick']
			address = presence['muc']['jid']
			address = str(address)
			if address == "": return
			#self.send_message(mto=presence['from'].bare,
					  #mbody="Hello, %s (%s)" %(nick, address),
					  #mtype='groupchat')
			self.lobby.nick_to_gmail[nick] = address[:address.find("@")]
	# }}}

	# Main components of the class DarkMafiaBot {{{1
	def registerGame(self, game):
		self.game = game
		self.game.master = self

	def mkRequest(self, name, **kwargs):
		self.viewer.update(name = name, **kwargs)
		print lib.colors.STARTCOLOR + name + lib.colors.ENDCOLOR + ":", kwargs

	def setPhaseTimer(self, delta):
		self.phase_timer.cancel()
		self.phase_timer = threading.Timer(delta, self.game.endPhase)
		self.phase_timer.start()
		self.next_time = time.time() + delta
		print lib.colors.STARTCOLOR + "TIMER" + lib.colors.ENDCOLOR + ":", delta

	def message(self, msg):
		if not msg['type'] in ('chat', 'normal', 'groupchat'):
			print "Unknown type " + msg['type']
			print msg
			return

		body = msg['body'].strip() + " "

		kwargs = {} # get various arguments {{{2
		kwargs['cmd_name'] = body[1:body.find(" ")].replace("!", "_").strip() # Name of command
		kwargs['request'] = body[body.find(" ")+1:].strip() # any arguments provided to the command
		kwargs['is_group'] = False if msg['type'] in ('chat', 'normal') else True # is MUC group chat?
		kwargs['msg'] = msg
		if kwargs['is_group']:
			kwargs['nick'] = msg['mucnick']
			kwargs['sender'] = self.lobby.nick_to_gmail.get(msg['mucnick'], None)
		else:
			kwargs['nick'] = ''
			address = msg['from'].bare
			kwargs['sender'] = address[:address.find("@")]
		kwargs['caster'] = self.game.p(kwargs['sender'])
		# }}}

		if body[0] == "\\": # convert backslashes to forward
			body = "/" + body[1:]

		if body[0] == "/":
			# send to various handlers {{{2
			print kwargs['sender'], body
			if kwargs['cmd_name'] in self.lobby.LOBBY_COMMANDS:
				return_status = self.lobby.handle(**kwargs)
				if return_status: msg.reply(str(return_status)).send()
			elif kwargs['cmd_name'] in self.viewer.VIEW_COMMANDS:
				return_status = self.viewer.handle(**kwargs)
				if return_status: msg.reply(str(return_status)).send()
			elif kwargs['cmd_name'] in self.CONTROLLER_COMMANDS:
				return_status = getattr(self, "handle_" + kwargs['cmd_name'])(**kwargs)
				if return_status: msg.reply(str(return_status)).send()
			else:
				if kwargs['caster'] is None:
					msg.reply("You are not registered in this game").send()
				else:
					kwargs['caster'].act(act_name = kwargs['cmd_name'], request = kwargs['request'])
			# }}}

		elif body[0:4] == "sudo":
			if not any([admin == str(kwargs['sender']) for admin in lib.ADMINS]):
				#msg.reply("%s not in %s" %(kwargs['sender'], lib.ADMINS)).send()
				return
			stuff = body[5:]
			cmd = stuff[:stuff.find(" ")].strip()
			arg = stuff[stuff.find(" ")+1:].strip()
			#if msg['type'] == 'groupchat': return
			if cmd == "eval":
				msg.reply(str(eval(arg))).send()
			elif cmd == "shutdown":
				self.shutdown()
			else:
				exec(stuff)
		else:
			# standard talk.  How to handle?
			kwargs['request'] = body # no command name
			if self.game.inProgress():
				if kwargs['caster'] is None:
					# outside talking - for now I'll let it slide
					pass
				elif not kwargs['caster'].alive and kwargs['is_group']:
					msg.reply(lib.DEAD_TALK_MSG).send() # dead talk
				elif self.game.daylight == 0 and kwargs['is_group'] and not kwargs['caster'].can_night_talk_public:
					msg.reply(lib.NIGHT_TALK_MSG).send() # night talk
				elif self.game.daylight == 0 and not kwargs['is_group']:
					kwargs['caster'].act(act_name = 'nighttalk', request = kwargs['request'])
				else:
					# OK, let the person speak
					pass
			elif not kwargs['is_group']:
				msg.reply("Use \\help to get help.").send()
				
	
	def handle_invite(self, **kwargs):
		self.plugin['xep_0045'].invite(self.room, kwargs['msg']['from'].bare, "Use this room to join the lobby.")
		return "Invited.  You can also join directly using %s." %(self.room)

	def shutdown(self):
		self.phase_timer.cancel()
		raise KeyboardInterrupt, "kthxbai"
	# }}}

# vim: foldmethod=marker
