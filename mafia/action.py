import lib
import traceback

class Action:
	queue = 0 # if this is set to 1, then queue to night instead
	priority = 0 # priority of a queued night action
	can_use_if_dead = 0 # prevent dead people from doing stuff

	def __init__(self, main, **kwargs):
		self.main = main
		for key in kwargs:
			setattr(self, key, kwargs[key])
	def __call__(self, caster, request=None):
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
		if self.queue:
			self.confirmReceived(caster, *args)
			caster.parent_game.submitNightAction(key=self.nGetKey(caster), priority=self.priority, caster=caster, args=(caster,)+args, action=self.main)
		else:
			try:
				return self.main(caster, *args)
			except TypeError:
				caster.quietLog("Error occurred while processing that request")
				print lib.colors.FAIL
				print traceback.print_exc()
				print "Caster is", caster
				print args
				print lib.colors.ENDCOLOR
	def confirmReceived(self, caster, *args):
		caster.parent_game.master.mkRequest(name = "command_received", caster = caster)
	def nGetKey(self, caster):
		# change this in a subclass
		# e.g. when Mafia kills, we want the night caster to be the Mafia, not the caster
		# otherwise Mafia could submit a kill per person
		return caster
	needs_alive = 1 # needs target alive
	
	def __repr__(self):
		funcRaw = str(self.main)
		funcName = funcRaw.split(' ')[1]
		return "Action " + funcName

class TargetAction(Action):
	def parser(self, caster, request):
		# Parses everything after the command name
		# e.g. "/kill ilovepink" then request="ilovepink"
		player = caster.parent_game.p(request)
		assert player is not None, "No such player"
		assert player.alive or not self.needs_alive, "Needs target to be alive."
		return (player,)
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
