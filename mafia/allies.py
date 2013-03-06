from action import TextAction, EmptyAction, Action

def func_change_channel(self, channel = "CYCLE"):
	if len(self.talk_channels) != 0:
		if channel == "CYCLE":
			self.talk_index += 1
			self.talk_index %= len(self.talk_channels) # talk_index should be mod length
		elif channel in self.talk_channels:
			self.talk_index = self.talk_channels.index(channel)
		else:
			self.quietLog("Hi, this isn't your channel kind sir.")
		self.quietLog("Now whispering in channel "+str(self.talk_channels[self.talk_index]))
	else:
		self.quietLog("You have no talk channels...")
action_change_channel = Action(func_change_channel, request_parser = lambda user, x: x if x else "CYCLE")

def func_view_channels(caster):
	caster.quietLog("You have access to nighttalk channels: " + ", ".join(caster.talk_channels) + ".")
action_view_channels = EmptyAction(func_view_channels)

def func_view_allies(caster):
	# quietLogs a list of allies
	caster.quietLog("The following players are allied with you in Channel %s:\n" %(caster.currentChannel()) \
			+ ', '.join(caster.getAllies()))
action_allies = EmptyAction(func_view_allies)

def func_night_talk(caster, text):
	parsedStr = "[NT] %s: %s" %(caster, text)
	allies = caster.getAllies()
	if len(allies) <= 1:
		caster.quietLog("You have no living allies remaining")
	for ally in caster.getAllies():
		if ally == caster: continue
		ally.quietLog(parsedStr)
action_night_talk = TextAction(func_night_talk)
