import getpass
import threading
import logging
import controller

import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser("Launcher for darkmafiabot")
	parser.add_argument('-j', '--jid', dest='jid', help='The JID to use')
	parser.add_argument('-s', '--status', dest='status', help='The status message to send out.')
	args = parser.parse_args()
	jid = 'darkmafiabot2013@gmail.com' if args.jid is None else args.jid
	status = 'This account is now running darkmafiabot alpha 2013.02; type \help for help.' if args.status is None else args.status
	
	logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
	bot = controller.DarkMafiaBot(password = getpass.getpass(), jid = jid, status = status)

	run = True
	if run:
		if bot.connect():
			main_thread = threading.Thread(target = bot.process, kwargs = {'block' : True}, name = "DarkMafiaBot Main Thread")
			main_thread.start()
			#bot.process(block = True)
			#bot.phase_timer.cancel()
		else:
			print "Unable to connect."

