from action import TargetAction, EmptyAction

def func_vote(caster, target):
	#Unvote former player
	
	#Vote new player
	caster.vote_target = target
	Lnum = int((caster.parent_game.num_alive/2)+1) - len(caster.vote_target.voters) # apparent lynch count
	caster.parent_game.master.mkRequest(name="vote_change", caster=caster, target=target, apparent_lynch_count=Lnum)

	#Check If Lynch
	#if caster.vote_target.num_votes_on > caster.parent_game.num_alive / 2:
	if caster.vote_target.num_votes_on > sum([t.vote_weight for t in caster.parent_game.player_list if t.alive == 1]) / 2:
		if caster.vote_target != caster.parent_game.the_no_lynch:
			if target.unlynchable == "NO":
				caster.parent_game.master.mkRequest(name="lynch_success", target=target)
				caster.parent_game.killPlayer(target, 
						reason = "Lynched Day " + str(caster.parent_game.day),
						surpress = 1)
				target.onLynch(caster)
			else:
				caster.parent_game.master.mkRequest(name="lynch_fail", target=target)
			caster.parent_game.checkIfWin()
			caster.parent_game.startNight()
		else:
			caster.parent_game.master.mkRequest(name="nolynch")
			caster.parent_game.startNight()
	return target
action_vote = TargetAction(func_vote)
	
def func_unvote(caster):
	#Unvote former player
	caster.vote_target = None
	caster.parent_game.master.mkRequest(name="unvote", caster=caster)
action_unvote = EmptyAction(func_unvote)

def func_votenolynch(caster):
	caster.act('vote', caster.parent_game.the_no_lynch)
action_votenolynch = EmptyAction(func_votenolynch)

