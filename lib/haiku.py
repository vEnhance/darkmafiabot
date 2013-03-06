import random

def haikuGet(gender=0):
	start = "There once was this guy. \n"

	choke = "He choked on " + random.choice([
		"a big fat steak",
		"a banana",
		"an apple tart",
		"mashed potatoes",
		"a piece of cake",
		"a dollar bill",
		"water bottles",
		"burning coffee",
		"some asbestos",
		"a bowl of soup",
		"a plastic bag",
		"an unknown food"
		])+"."

	disease = "He got "+random.choice([
		"the mad cow disease",
		"rabies from a dog",
		"terminal cancer",
		"hypothermia",
		"zapped into a frog",
		"an uncommon cold",
		"an unknown disease",
		])+"."

	# Going to comment out some of the more boring ones... -- Evan
	mid = random.choice(["He was electrocuted.",
		"He was drowned in much water.",
		"Curiosity got him.",
		"He was crushed by falling rocks.",
		"Tried to divide by zero.",
		"Nanobots consumed him up.",
		"How'd he die? I do not know.",
		"He was hung by the townies.",
		"Assassination occurred.",
		"Nuclear launch detected.",
		choke,
		"Somebody tried CPR.",
		"CERN accident.",
		"Attacked by dictionaries.",
		"Hyperinflation got him.",
		"A lightning beam struck him down.",
		"Confused, he then hit himself.",
		"Died from hyperhydration.",
		"He died from malnourishment.",
		"A bee stung him fatally.",
		"A car just ran him over.",
		"His airplane crashed into sea.",
		"He died from suffocation.",
		"He committed suicide.",
		# "Blown up by a hand grenade.",
		"He was hit by a TV.",
		# "Well, the wrecking ball went splat.",
		# "He fell face-first into spikes.",
		"Well, his brain surgeon said \"Oops.\"",
		"By Grammar Nazis, killed he!",
		"Ejected from the airlock.",
		"<insert commercial break here>",
		"The haiku police executed him for not making a haiku.",
		disease,
		"Two words: antimatter bomb.",
		"The banhammer fell on him.",
		"He was zapped by wand of death.",
		# "A car crash. He was in it.",
		"Guns didn't kill him, I did!",
		# "He was impaled by a sword.",
		"He was hacked. Literally.",
		# "Whoops, his life support cord broke.",
		"Disproved his own existence.",
		"Oh, that's what this button does.",
		"He was bitten by a snake.",
		"He had too much alcohol.",
		"Zombies materialized.",
		"He had to write an essay.",
		"He had to write an essay.", # this needs to appear more
		"An unknown force has killed him.",
		"He hurt himself in confusion!",
		"He used the move: Selfdestruct!",
		"Power too overwhelming.",
		"Then a bunch of zerglings spawned.",
		"He was turned into a rock.",
		"He was turned into a stone.",
		"No usable Pokemon.",
		"<there's no killing in this game>",
		"The result was very ugly.",
		"The Mafia sent him to jail.",
	])

	end_adj = random.choice([
		"sad",
		"bad",
		"fail",
		"quick",
		"swift",
		"short",
		"long",
		"pained",
		"weird",
		"odd",
		"lolz",
		"meh",
		"strange",
		"cool",
		"loud",
		"qq"
	])

	end = "He died a"+("n" * ("aeiou".count(end_adj[0])))+" "+end_adj+" death."
	if gender == 1:
		start = start.replace("guy", "girl")
		end = end.replace("He ", "She ")
		mid = mid.replace(" he", " she")
		mid = mid.replace("He ", "She ")
		mid = mid.replace(" his", " her")
		mid = mid.replace("His ", "Her ")
		mid = mid.replace(" him", " her")
	
	haiku = start + mid + "\n" + end
		
	return haiku
	
