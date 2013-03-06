# 
import random
from player import Player
from action import EmptyAction, TextAction, TargetAction
from lib import ERROR_BAD_USE

# Low level stuff {{{1

STANDARD_TOWN_ALIGNED_PM = "\nYou win if and only if all non-town members are eliminated."
STANDARD_MAFIA_ALIGNED_PM = "\nYou are mafia-aligned. You win if all non-mafia members are eliminated. Note that the opposing Mafia faction, if any, must also be eliminated.  You can check your partners with the command \"/allies\"."
STANDARD_SK_ALIGNED_PM = "\nYou are SK-aligned.  You win if and only if you are the only player alive."

# Vanilla roles (town/mafia/vig/doctor/cop {{{1
#Vanilla roles {{{2
class Town(Player):
	align = 0
	ialign = 0
	player_type = "VANILLA TOWNIE"
	rolePM = "You are a Vanilla Townie. You have no night action or nonstandard day actions." + STANDARD_TOWN_ALIGNED_PM

# Killer/mafia roles {{{2
def func_kill(caster, target):
	target.addDeathMark(by=caster, day=caster.parent_game.day)
action_mafia_kill= TargetAction(func_kill, queue=1, priority=99, nGetKey = lambda c: "MAFIA" + str(c.align))

class Mafia(Player):
	align = 1
	ialign = 1
	talk_channels = ["MAFIA 1"]
	player_type = "MAFIA GOON"
	rolePM = "You are one of the Mafia. You can kill at night with the command \"/kill username\"." + STANDARD_MAFIA_ALIGNED_PM
	night_methods = dict(Player.night_methods, kill=action_mafia_kill)

class VanillaMafia(Mafia):
	player_type = "VANILLA MAFIA GOON"
	rolePM = "You are one of the Mafia, but you cannot kill; one of your superiors will do that." + STANDARD_MAFIA_ALIGNED_PM
	
class MafiaII(Mafia):
	align = 101
	talk_channels = ["MAFIA 2"]
	player_type = "TYPE 2 MAFIA GOON"
	rolePM = "You are one of the Mafia of a different Mafia Faction." + STANDARD_MAFIA_ALIGNED_PM

class Werewolf(Mafia):
	align = 1001
	talk_channels = ["WOLF 1"]
	player_type = "WEREWOLF"
	rolePM = "You are one of the Werewolf of the Wolf Faction. \n You are wolf-aligned. You win if all non-wolf members are eliminated. You can check your partner list with the command \"/getpartners\". You can kill at night with the command \"/kill username\"."	


action_vig_kill = TargetAction(func_kill, queue=1, priority=99)
class Vigilante(Town):
	player_type = "NIGHT VIGILANTE"
	rolePM = "You are a Vigilante. You can kill people at night using \"/vig username\"." + STANDARD_TOWN_ALIGNED_PM
	night_methods = dict(Town.night_methods, vig = action_vig_kill)

# Healing roles {{{2
def func_protect(self, target):
	if self.prev_save[0] == target and self.prev_save[1] == self.parent_game.day-1 and self.overdose == 1:
		#self.parent_game.pubLog("Overdose %s" %target)
		self.parent_game.killPlayer(target, "Overdosed Night %d" %(self.parent_game.day-1), surpress=1)
		#target.deathMarks += [self.parent_game.day]
	elif self.overdose == 0 and self == target:
		pass
	else:
		self.prev_save = (target, self.parent_game.day)
		if target.bulletproof == "NO":
			target.bulletproof = "TONIGHT"
action_protect = TargetAction(func_protect, queue=1, priority=50)

class Doctor(Town):
	player_type = "DOCTOR"
	prev_save = (None, 0)
	overdose = 1
	rolePM = "You are a Doctor. You can protect someone from any kill at a night with the command \"/protect username\". However, if you protect someone in two consecutive nights, the target is killed." + STANDARD_TOWN_ALIGNED_PM
	night_methods = dict(Town.night_methods, protect = action_protect)

class NoODDoctor(Doctor):
	player_type = "DOCTOR"
	prev_save = (None, 0)
	overdose = 0
	rolePM = "You are a Non-overdose Doctor. You can protect someone from any kill at a night with the command \"/protect username\". However, you cannot protect yourself. \n You are town-aligned. You win if all non-town members are eliminated."

# }}}
# Inspection roles {{{2
def func_inspect(self, target):
	theRes = self.sanity_func(target.ialign)
	self.quietLog("Inspected %s and recieved result %s." %(target,("INNOCENT", "GUILTY")[theRes]))
action_inspect = TargetAction(func_inspect, queue=1, priority=50)

class GeneralCop(Town):
	player_type = "COP"
	night_methods = dict(Town.night_methods, inspect=action_inspect, investigate=action_inspect)
	rolePM = "You are a Cop, but you do not know your sanity. You can investigate someone during the night with the command \"/investigate username\" or \"/inspect username\"." + STANDARD_TOWN_ALIGNED_PM

class CertainSaneCop(GeneralCop):
	rolePM = "You are a Sane Cop. You can investigate someone during the night with the command \"/investigate username\" or \"/inspect username\"." + STANDARD_TOWN_ALIGNED_PM
	player_type = "SANE COP"
	sanity_func = lambda self, x: int(x!=0)

# Note: the following roles are uncertain
# That is, cops do not know their own sanity
# and sanities are not revealed on death.
class SaneCop(GeneralCop):
	sanity_func = lambda self, x: int(x!=0)

class InsaneCop(GeneralCop):
	sanity_func = lambda self, x: int(x==0)

class NaiveCop(GeneralCop):
	sanity_func = lambda self, x: 0

class ParanoidCop(GeneralCop):
	sanity_func = lambda self, x: 1
	
class SchizophrenicCop(GeneralCop):
	def endow(self):
		self.initial_sanity = random.randrange(0,2)
	sanity_func = lambda self, x: (int(x!=0)+self.parent_game.day+self.initial_sanity)%2

class RandomCop(GeneralCop):
	def endow(self):
		self.sanity_func = lambda self, x: random.randrange(0,2)

class RevealOnDeathCop(GeneralCop):
	lying_role = 1

class RODSaneCop(RevealOnDeathCop):
	sanity_func = lambda self, x: int(x!=0)
	player_type = "SANE COP"
	alt_player_type = "COP"

class RODInsaneCop(RevealOnDeathCop):
	sanity_func = lambda self, x: int(x==0)
	player_type = "INSANE COP"
	alt_player_type = "COP"

class RODNaiveCop(RevealOnDeathCop):
	sanity_func = lambda self, x: 0
	player_type = "NAIVE COP"
	alt_player_type = "COP"

class RODParanoidCop(RevealOnDeathCop):
	sanity_func = lambda self, x: 1
	player_type = "PARANOID COP"
	alt_player_type = "COP"
	
class RODSchizophrenicCop(RevealOnDeathCop):
	def endow(self):
		self.initial_sanity = random.randrange(0,2)
	sanity_func = lambda self, x: (int(x!=0)+self.parent_game.day+self.initial_sanity)%2
	player_type = "SCHIZOPHRENIC COP"
	alt_player_type = "COP"

class RODRandomCop(RevealOnDeathCop):
	sanity_func = lambda self, x: random.randrange(0,2)
	player_type = "RANDOM COP"
	alt_player_type = "COP"

class RODRandomDethyCop(GeneralCop):
	alt_player_type = "COP"
	def endow(self):
		self.initial_sanity = random.randrange(0,4)
		if self.initial_sanity < 2:
			self.sanity_func = lambda self, x: self.initial_sanity
			if self.initial_sanity == 0:
				self.player_type = "NAIVE COP"
			else:
				self.player_type = "PARANOID COP"
		elif self.initial_sanity == 2:
			self.sanity_func = lambda self, x: int(x==0)
			self.player_type = "INSANE COP"
		else:
			self.sanity_func = lambda self, x: int(x!=0)
			self.player_type = "SANE COP"


# Roleblockers {{{2
def func_roleblock(self, target):
	if self.roleblocked == "NO":
		target.roleblocked = "TONIGHT"
action_roleblock = TargetAction(func_roleblock, queue=1, priority=0)

#Blocking Roles
class MRoleBlocker(Mafia):
	player_type = "MAFIA ROLEBLOCKER"
	rolePM = "You are a Mafia Roleblocker. You can roleblock anyone during the night with the command \"/roleblock username\"; they will not be able to perform any action at the night you blocked them." + STANDARD_MAFIA_ALIGNED_PM
	night_methods = dict(Mafia.night_methods, roleblock=action_roleblock)

class TRoleBlocker(Town):
	player_type = "ROLEBLOCKER"
	rolePM = "You are a Roleblocker. You can roleblock anyone during the night with the command \"/roleblock username\"; they will not be able to perform any action at the night you blocked them." + STANDARD_TOWN_ALIGNED_PM
	night_methods = dict(Mafia.day_methods, roleblock=action_roleblock)


# }}}
# Standard weirdness {{{1
# Alignment roles {{{2
class Mason(Town):
	talk_channels = ["MASON 1"]
	player_type = "MASON"
	rolePM = "You are a Mason. You can talk to other Masons at night. You can check your partner list with the command \"/getpartners\". \n You are town-aligned. You win if all non-town members are eliminated."

# Killer roles {{{2
#Day kills
def func_dayvig(self, victim):
	if self.bulletUsed == 1:
		self.quietLog("You already used your bullet")
		return ERROR_BAD_USE
	if victim.bulletproof == "NO" and victim.alive == 1:
		self.parent_game.killPlayer(victim, "Killed" + " " + self.parent_game.getCurrentPhase())
		self.bulletUsed = 1
	elif victim.bulletproof != "NO" and victim.alive == 1:
		self.parent_game.pubLog("An attempt to kill %s was foiled!" %victim)
		self.bulletUsed = 1
action_dayvig = TargetAction(func_dayvig)

def func_mafiaDaykill(self, victim):
	if self.daybulletLastUsed == self.parent_game.day:
		self.quietLog("You cannot perform multiple daykills")
		return ERROR_BAD_USE
	if victim.bulletproof == "NO" and victim.alive == 1:
		self.parent_game.killPlayer(victim, "Killed" + " " + self.parent_game.getCurrentPhase())
	elif victim.bulletproof != "NO" and victim.alive == 1:
		self.parent_game.pubLog("An attempt to kill %s was foiled!" %victim)
	else:
		pass
	self.daybulletLastUsed = self.parent_game.day
	self.roleblocked = "TONIGHT"
action_daykill = TargetAction(func_mafiaDaykill)	


class DayVig(Town):	
	player_type = "DAY VIGILANTE"
	rolePM = "You are a Day Vigilante. You can kill someone during the day with the command \"/dayvig username\". You may only use this ability once in your game. Your kills will show up with a generic \"Killed Day X\"." + STANDARD_TOWN_ALIGNED_PM
	bulletUsed = 0
	day_methods = dict(Town.day_methods, dayvig = action_dayvig)
	
class CrazedFiend(Mafia):
	player_type = "CRAZED FIEND"
	rolePM = "You are a Crazed Fiend. You are one of the Mafia but you may kill during the day. You can kill someone during the day with the command \"/daykill username\". However, if you choose to daykill, all night actions you submit will fail. Your daykill is indistinguishable from that of a vigilante. \n You are mafia-aligned. You win if all non-mafia members are eliminated. You can check your partner list with the command \"/getpartners\". You can kill at night with the command \"/kill username\"."
	daybulletLastUsed = 0
	day_methods = dict(Mafia.day_methods, dayvig = action_daykill)
	
	
	

# SK align {{{2

#Parent class
#DONOTUSE
class SKAlign(Player):
	align = -1
	ialign = 1

action_sk_kill = TargetAction(func_kill, queue=1, priority=99)

class SerialKiller(SKAlign):
	player_type = "SERIAL KILLER"
	rolePM = "You are a Serial Killer. You can kill people at night using \"/kill username\"." + STANDARD_SK_ALIGNED_PM
	night_methods = dict(SKAlign.night_methods, kill = action_sk_kill)

class SoreLoser(SKAlign):
	player_type = "SORE LOSER"
	rolePM = "You are a sore loser.  You win if and only if you are the last person alive.  If you are lynched, the person who cast the last vote dies.  Not that it helps you."
	def onLynch(self, caster):
		self.parent_game.killPlayer(caster, "Kidnapped " + self.parent_game.getCurrentPhase())

# Jesters, bombers, vengeful, ... {{{2
class Survivor(Town):
	align = -2 #Not factored in win condition.
	ialign = 0
	player_type = "SURVIVOR"
	rolePM = "You are a Survivor. You win if and only if you are alive when the game ends (only a faction remains)."

class Jester(Town):	
	align = -2 #Not factored in win condition.
	ialign = 0
	explosive = 1
	player_type = "JESTER"
	rolePM = "You are a Jester. You win if and only if you are lynched. (Note that you must be lynched, not killed in any other way, to win.)"
	def onLynch(self, caster):
		self.parent_game.pubLog("Oh no! You lynched the Jester!")
		if self.explosive == 1:
			self.parent_game.runGameOver()

class BigGameJester(Jester):
	explosive = 0	

def attr_func_bomb(self, caster):
	self.parent_game.killPlayer(caster,
			"Bombed " + self.parent_game.getCurrentPhase(),
			surpress = 1)
class Bomber(Town):
	player_type = "BOMBER"
	rolePM = "You are a Bomber. If you are lynched, the person who casts the last vote on you is also killed." + STANDARD_TOWN_ALIGNED_PM
	onLynch = attr_func_bomb


# n-voters {{{2
class NoVoter(Town):
	vote_weight = 0
	player_type = "NOVOTER"
	rolePM = "You are a No-voter Townie. While it will not be immediately evident to everyone else, the weight of your vote is 0. \n You are town-aligned. You win if all non-town members are eliminated."
	
class DoubleVoter(Town):
	vote_weight = 2
	player_type = "DOUBLEVOTER"
	rolePM = "You are a Double-voter Townie. While it will not be immediately evident to everyone else, the weight of your vote is 2. \n You are town-aligned. You win if all non-town members are eliminated."
	
class AntiVoter(Town):
	vote_weight = -1
	player_type = "ANTIVOTER"
	rolePM = "You are an Anti-voter Townie. While it will not be immediately evident to everyone else, the weight of your vote is -1. \n You are town-aligned. You win if all non-town members are eliminated."
	
class RandomVoter(Town):
	vote_weight = random.randint(-2,2)
	player_type = "RANDOMVOTER"
	rolePM = "You are a Random-voter Townie. The weight of your vote varies. Your vote weight might make the target immediately lynched (your vote weight is a large positive number) or make the target cannot be lynched (your vote weight is a large negative number). Maybe, if we (the developers) are having fun tinkering the roles. :) \n You are town-aligned. You win if all non-town members are eliminated."
	
class HalfVoter(Town):
	vote_weight = .5
	player_type = "HALFVOTER"
	rolePM = "You are a Half-voter Townie. While it will not be immediately evident to everyone else, the weight of your vote is 0.5. \n You are town-aligned. You win if all non-town members are eliminated."

class TripleVoter(Town):
	vote_weight = 3
	player_type = "TRIPLEVOTER"
	rolePM = "You are a triple-voter townie. While it will not be immediately evident to everyone else, the weight of your vote is 3. \n You are town-aligned. You win if all non-town members are eliminated."

# Misc {{{2
def func_jailkeep(self, target):
	func_roleblock(self, target)
	func_protect(self, target)
action_jailkeep = TargetAction(func_jailkeep, queue=1, priority=11)
	
class Jailkeeper(Town):
	player_type = "JAILKEEPER"
	rolePM = "You are a Jailkeeper. You may protect someone every night, but you will also block any actions that they perform. You can jailkeep someone during the night with the command \"/jailkeep username\". \n You are town-aligned. You win if all non-town members are eliminated."
	prev_save = (None, 0)
	overdose = 0
	night_methods = dict(Town.night_methods, jailkeep = action_jailkeep)

##EXPERIMENTAL
def func_mup(self, target):
	self.quietLog("Random action is being performed on %s" %target)
	actionList = [(func_kill,99), (func_protect,50), (func_inspect,50)]
	action, priority = random.choice(actionList)
	
	self.parent_game.submitNightAction(self.pid, priority, user=self, args = [self,target], action = action)
action_mup = TargetAction(func_mup)


class MUP(Town):
	player_type = "MULTIPLE USER PERSONALITY"
	rolePM = "You are a Multiple User Personality. Every night you may target someone. The target will be either inspected, killed, or protected with equal probability. You can MUP-target someone with the command \"/mup username\"." + STANDARD_TOWN_ALIGNED_PM
	prev_save = (None, 0)
	overdose = 1
	sanity_func = lambda self, x: int(x!=0)
	night_methods = dict(Town.night_methods, mup = action_mup)

class InsaneMUP(MUP):
	sanity_func = lambda self, x: int(x==0)	
	
class IndepMUP(MUP):
	align = -1
	rolePM = "You are a Multiple User Personality. Every night you may target someone. The target will be either inspected, killed, or protected with equal probability. You can MUP-target someone with the command \"/mup username\"." + STANDARD_SK_ALIGNED_PM


# }}}
# mafiabot-only roles {{{1
# Anti-Jester {{{2
def func_findjesters(self):
	if [t.public_name for t in self.parent_game.playerList if t.player_type in ["JESTER","FOOL"]] == []:
		return_msg = "There are no jesters."
	else:
		return_msg = "The jesters are " + " and ".join([t.public_name for t in self.parent_game.playerList if t.player_type in ["JESTER","FOOL"]]) + "."
	self.quietLog(return_msg)
action_findjesters = EmptyAction(func_findjesters)
	
class AntiJester(Town):
	vote_weight = -1
	player_type = "ANTIJESTER"
	rolePM = "You are an Anti-Jester. You can find all jesters in the game with the command \"/find\". In addition, you have a vote weight of -1." + STANDARD_TOWN_ALIGNED_PM
	day_methods = dict(Town.day_methods, find = action_findjesters)

# Vote-screwing! {{{2
def func_bribe(self, target):
	#Return vote
	if self.prev_target is not None:
		self.prev_target.vote_weight += 1
		self.vote_weight -= 1
	if target.vote_weight > 0:
		target.vote_weight -= 1
		self.vote_weight += 1
	self.prev_target = target
action_bribe = TargetAction(func_bribe, queue=1, priority=50)
	
class Politician(Town):
	player_type = "POLITICIAN"
	rolePM = "You are a Politician. You can steal the vote of any user for the following day during the night with the command \"/bribe user\". (The user will not be notified.)" + STANDARD_TOWN_ALIGNED_PM
	night_methods = dict(Town.night_methods, bribe = action_bribe)
	prev_target = None

class MafiaPolitician(Mafia):
	player_type = "MAFIA POLITICIAN"
	rolePM = "You are a Mafia Politician. You can steal the vote of any user for the following day during the night with the command \"/bribe user\". (The user will not be notified.)" + STANDARD_MAFIA_ALIGNED_PM
	night_methods = dict(Mafia.night_methods, bribe = action_bribe)
	prev_target = None
	
def func_motivate(self, target):
	if self.prev_target != None:
		self.prev_target.vote_weight -= 1
	if self.pid == target.pid:
		return
	target.vote_weight += 1
	self.prev_target = target

action_motivate = TargetAction(func_motivate, queue=1, priority=50)
	
class Motivator(Town):
	player_type = "MOTIVATOR"
	rolePM = "You are a Motivator. You may motivate a user (other than yourself) during the night with the command \"/motivate user\". (The user will not be notified.) The user will have an extra vote the following day.\nIf you target yourself, then no user will gain an extra vote.  If you do not target anyone, it is assumed you motivate the same player." + STANDARD_TOWN_ALIGNED_PM
	prev_target = None
	night_methods = dict(Town.night_methods, motivate = action_motivate)

def func_cure(self, target):
	self.cured = self.cured + [target]
action_cure = TargetAction(func_cure, queue=1, priority=50)	

# Plague Doctor {{{2
class PlagueDoctor(Town):
	vote_weight = 2
	player_type = "PLAGUEDOCTOR"
	rolePM = "You are a Plague Doctor. Currently there is a disease that has infected everyone in the town. You can cure someone every night with the command \"/cure username\". If you die, then everyone with the disease dies with probability 70%. In addition, you are a double-voter." + STANDARD_TOWN_ALIGNED_PM
	night_methods = dict(Town.night_methods, cure=action_cure)
	cured = []
	def onDeath(self):
		self.parent_game.pubLog("UHOH")
		# Goes through each player
		for currPlayer in [player for player in self.parent_game.playerList if (player != self and not player in self.cured)]:
			if random.uniform(0,1) <= 0.7:
				self.parent_game.killPlayer(currPlayer, "Died of the plague.", surpress = 1)
		self.parent_game.checkIfWin()

# RPS {{{2
def func_rpsset(self, text):
	if text.lower() in ["rock", "paper", "scissors"]:
		self.type = text.lower()
		self.quietLog("Set type to %s." %self.type)
	else:
		self.quietLog("Bad choice.")
		return ERROR_BAD_USE
def func_rpsaim(self):
	self.canFire = 1
	self.quietLog("OK")
def func_rpsfire(self, target):
	if self.canFire != 1:
		#Do nothing
		self.quietLog("Aim first.")
		return ERROR_BAD_USE
	else:
		self.canFire = 0
		self.parent_game.pubLog("*%s attacks %s!*" %(self, target))
		if (self.type, target.type) in [("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")]:
			self.parent_game.killPlayer(target, "Defeated by %s." %self)
		elif self.type == target.type:
			self.parent_game.pubLog("Oops both are %s!  Gogogo!" %self.type)
		else:
			self.quietLog("Nope, he's a %s." %target.type)
			target.quietLog("You survived.  %s is currently %s." %(self, self.type))
	
		
action_rpsset = TextAction(func_rpsset)
action_rpsaim = EmptyAction(func_rpsaim)
action_rpsfire = TargetAction(func_rpsfire)

class RPS(Player):
	align = -1
	player_type = "RPS GUNFIGHTER"
	type = "rock"
	canFire = 0
	day_methods = {'set' : action_rpsset, 'aim' : action_rpsaim, 'fire': action_rpsfire}
	rolePM= "You are an RPS GUNFIGHTER.  Everyone else in this game is also (supposed to be) an RPS gunfighter.  You win if you are the last one alive.\n\n You have three methods. \n /set <type> sets your type to either rock, paper, or scissors. \n /aim is a bottleneck that you must type every time prior to /fire. \n /fire <player> kills the target if and only if your type beats their type. \n\n You may set your type as many times as you wish; previous types are overriden. The default type is \"rock\"."

# Misc roles {{{2
	
def func_evil(self, text):
	self.parent_game.pubLog("*[MAFIA]* " + text)
action_evil = TextAction(func_evil)
	
class EvilRadioman(Mafia):
	player_type = "EVIL RADIOMAN"
	rolePM = "You are an Evil Radioman. You can communicate to the town anonymously. Use the command \"/evil message\" to broadcast a message anonymously to the town." + STANDARD_MAFIA_ALIGNED_PM
	day_methods = dict(Mafia.day_methods, evil = action_evil)
	night_methods = dict(Mafia.night_methods, evil = action_evil)


# }}}
# }}}
# vim: foldmethod=marker
