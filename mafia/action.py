import lib
import traceback

class Action:
	queue = 0 # if this is set to 1, then queue to night instead
	priority = 0 # priority of a queued night action
	can_use_if_dead = 0 # prevent dead people from doing stuff
	max_uses = -1 # -1 if infinite, otherwise positive integer
	# by design, this attribute is never read again for determining routine procedures
	# instead, it is copied to the Player object and read there

	def __init__(self, main, **kwargs):
		self.main = main
		for key in kwargs:
			setattr(self, key, kwargs[key])
	def __call__(self, caster, name, request=None):
		if not caster.alive and not self.can_use_if_dead:
			caster.quietLog("Dead men tell no tales!")
			return lib.ERROR_BAD_USE
		# request denotes the content of the caster's message after 
		if request == "" or request is None:
			args = ()
		else:
			try:
				args = self.parser(caster, request)
			except AssertionError as e:
				caster.quietLog(e[0])
				return lib.ERROR_BAD_USE
		# Check num_uses
		if caster.num_left[name] == -1: pass # Irrelevant
		elif caster.num_left[name] == 0:
			caster.quietLog("This ability has been used the maximum number of times.  No further use is permitted.")
			return lib.ERROR_BAD_USE
		else:
			caster.quietLog("OK, this command has %d uses remaining." %(caster.num_left[name]-1))
		# If night action, submit to the game's queue
		if self.queue:
			self.confirmReceived(caster, *args)
			#Submit the night action
			caster.parent_game.submitNightAction(
					key = self.nGetKey(caster),
					priority = self.priority,
					caster = caster,
					args = (caster,)+args,
					action = self.main,
					name = name)
		else:
			# Reduce number of uses if not a one-shot action
			if caster.num_left[name] != -1: caster.num_left[name] -= 1
			try:
				return self.main(caster, *args)
			except TypeError:
				caster.quietLog("Error occurred while processing that request")
				print lib.colors.FAIL
				print traceback.print_exc()
				print "Caster is", caster
				print args
				print lib.colors.ENDCOLOR
	def checkOtherConditions(self, caster, *args):
		"""Called after arguments are parsed.  If an assertion is thrown here, the action is aborted.  Overload this to restrict actions."""
		pass
	def confirmReceived(self, caster, *args):
		caster.parent_game.master.mkRequest(name = "command_received", caster = caster)
	def nGetKey(self, caster):
		# change this in a subclass
		# e.g. when Mafia kills, we want the night caster to be the Mafia, not the caster
		# otherwise Mafia could submit a kill per person
		return caster
	needs_alive = 1 # needs target alive
	
	def __repr__(self):
		func_raw = str(self.main)
		func_name = func_raw.split(' ')[1]
		return "Action " + func_name

class TargetAction(Action):
	def parser(self, caster, request):
		# Parses everything after the command name
		# e.g. "/kill ilovepink" then request="ilovepink"
		player = caster.parent_game.p(request)
		assert player is not None, "No such player"
		assert player.alive or not self.needs_alive, "Needs target to be alive."
		return (player,)
# class DualTargetAction(Action):
	# def parser(self, caster, request):
		# Parses everything after the command name
		# e.g. "/kill ilovepink" then request="ilovepink"
		# r=request
		# player = caster.parent_game.p(r[0])
		# assert player is not None, "No such player"
		# assert player.alive or not self.needs_alive, "Needs target to be alive."
		# player1 = caster.parent_game.p(r[1])
		# assert player1 is not None, "No such player"
		# assert player1.alive or not self.needs_alive, "Needs target to be alive."
		# return (player,player1)
class TextAction(Action):
	def parser(self, caster, request):
		return (request,)
class EmptyAction(Action):
	def parser(self, caster, request):
		return ()


class Item(Action):
	#TODO do this.
	pass

# vim: fdm=marker
