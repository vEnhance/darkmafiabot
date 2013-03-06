# Mafia setups!
from game import MafiaGame
import roles
import random

# Shortcut
def make(name, setup):
	return MafiaGame(setup, game_name = name)

def setup_vanilla(m, n):
	"""VANILLA:
	This constructor accepts two arguments, m and n, which must be positive integers obeying m < n.
	It creates a game with m mafia and n VT's."""
	m = int(m)
	n = int(n)
	assert m > 0, "m must be a positive integer."
	assert n > 0, "n must be a positive integer."
	assert m < n, "The Mafia may not outnumber the Townies."
	return make("Vanilla with %d/%d Mafia" %(m, m+n),
			[roles.Mafia(private_name = "Mafia %d" %i) for i in range(m)] + [roles.Town(private_name = "Town %d" %i) for i in range(n)]
			)

def setup_hmmt2013():
	"""HMMT 2013:
	This constructor accepts no arguments.  A TYPEERROR occurs if any are given.
	It creates a setup consisting of 2 VT's, 2 Mafia, a town-aligned Bomber and a DoubleVoter."""
	game = make("HMMT 2013", [roles.Town(), roles.Town(), roles.Mafia(), roles.Mafia(), roles.Bomber(), roles.DoubleVoter()])
	names = ["Michael Kural", "Eugene Chen", "Andrew He", "Scott Wu", "Lewis Chen", "Jerry Wu"]
	random.shuffle(names)
	for i in range(6):
		game[i].private_name = names[i]
	return game

def setup_troll3():
	"""Troll-3:
	This constructor accepts no arguments.  TV/SL/M."""
	return make("Troll-3", [roles.SoreLoser("SL"), roles.TripleVoter("TV"), roles.Mafia("M")])

def setup_skonly(n):
	"""SK-ONLY:
	Takes a positive integer n>=3 and creates n serial killers."""
	n = int(n)
	assert n >= 3, "n must be at least 3"
	return make("SK-only", [roles.SerialKiller("Sellke") for i in range(n)])

def setup_supersaint(m, n):
	"""SUPERSAINT
	This constructor accepts two arguments, m and n, which must be positive integers obeying m <= n.
	It creates a game with m mafia, n VT's."""
	m = int(m)
	n = int(n)
	assert m > 0, "m must be a positive integer."
	assert n > 0, "n must be a positive integer."
	assert m <= n, "m cannot exceed n."
	return make("Supersaint", 
			[roles.Mafia("Mafia %d" %i) for i in range(m)] + [roles.Town("Town %d" %i) for i in range(n)] + [roles.Bomber("Zork")]
			)

def setup_rps(n):
	"""RPS-GUNFIGHT
	Creates an RPS-gunfight with n players (n>=2)"""
	n = int(n)
	assert n >= 2, "n >= 2"
	game = make("RPS with %d Players" %n, [roles.RPS("Rochambo") for i in range(n)])
	game.nightless = 1
	return game

def setup_dethy():
	"""DETHY
	Standard dethy."""
	return make("Dethy",[
		roles.SaneCop("Chen"),
		roles.InsaneCop("Chen"),
		roles.NaiveCop("Chen"),
		roles.ParanoidCop("Chen"),
		roles.SerialKiller("Lin")
		])



# vim: foldmethod=indent
# vim: foldnestmax=1
