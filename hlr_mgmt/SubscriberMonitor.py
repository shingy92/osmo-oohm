#!/usr/bin/python

###
#   Copyright (C) 2013
#   Fraunhofer Institute for Open Communication Systems (FOKUS)
#   Competence Center NETwork research (NET), St. Augustin, GERMANY
#       Alton MacDonald <alton.kenneth.macdonald@fokus.fraunhofer.de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
###

import sys, sqlite3, logging
import threading, time
import collections
from datetime import datetime, timedelta

from telnet_backend import telnet_backend

log = logging.getLogger(__name__)

class SubscriberMonitor(threading.Thread):
	## Initialization and Settings ##
	
	def __init__(self, provider_name, db, ip="127.0.0.1", port=4242):
		threading.Thread.__init__(self)
		self.provider = provider_name
		self.HLR_DB = db
		self.bsc_conn = telnet_backend(ip, port)
		self.active_subscribers	= collections.defaultdict()
		self.active = True
		
	def is_running(self):
		return self.active
		
	def connect_to_db(self):
		self.sqlconn = sqlite3.connect(self.HLR_DB, check_same_thread = False)
		self.cursor = self.sqlconn.cursor()

	def disconnect_from_db(self):
		try:
			self.sqlconn.close()
		except:
			pass

	def run(self):
		self.connect_to_db()
		self.get_active_subs()
		while(self.active):
			try:
				self.check_new_subs()
				self.get_active_subs()
			except sqlite3.OperationalError:
				pass	
			time.sleep(60)
	def stop(self):
		self.active = False
		self.active_subscribers	= collections.defaultdict()
		self.disconnect_from_db()

	def restart(self):
		self.stop()
		self.active = True
		self.connect_to_db()

	def get_active_subs(self):
		# query active subscribers
	 	self.cursor.execute("select * from subscriber where authorized=1 and lac>0")
	 	result = self.cursor.fetchall()
		if len(result)>0:
			for subscriber in result:
				#implicitly adds and updates subscribers with their expire_lu parameter
				self.active_subscribers[subscriber[5]]=subscriber[9]

	def check_new_subs(self):
		# authorized=1 checks for authorized subscribers
		# updated>datetime(...) checks for updates in the last minute
		# lac value greater than 0 indicate the phone is active
		#sqlIndex = [0 , 1      , 2      , 3   , 4   , 5        , 6         , 7   , 8  , 9        ]
		#sqlValue = (id, created, updated, imsi, name, extension, authorized, tmsi, lac, expire_lu)

		# query updated subscriber entries
		self.cursor.execute("select * from subscriber where authorized=1 and lac>0 and updated>datetime('now','-1 minute')")
		result = self.cursor.fetchall()
		self.bsc_conn.connect()
		if len(result)>0 and self.bsc_conn.connected:
			for subscriber in result:
				if not self.active_subscribers.has_key(subscriber[5]):
					# new subscriber
						self.bsc_conn.send_welcome_sms(self.provider, subscriber[5])
				else:
					# workaround for excessive premature updates cause by expire_lu values
					# expire_lu tells OpenBSC when to update our subscriber entries
					# unfortunately it is set to 1 hour after after each update is made
					# so we have to ignore sending sms messages each hour to our already subscribed users
					updated = datetime.strptime(subscriber[2],"%Y-%m-%d %H:%M:%S")
					expected = datetime.strptime(self.active_subscribers[subscriber[5]],"%Y-%m-%d %H:%M:%S")
					diff = updated-expected
					if diff > timedelta(hours=1):
						# returning subscriber (roaming/out-of-range/?)
						self.bsc_conn.send_welcome_sms(self.provider, subscriber[5])
			self.bsc_conn.close()

def main():
	if len(sys.argv)<3:
		print "ERROR: not enough arguments\n"
		print "USAGE: python " + sys.argv[0] + " provider_name /path/to/hlr_db.sqlite3 [openbsc_ip] [openbsc_port]\n"
		exit(1)
	if len(sys.argv)==3:
		subMonitor = SubscriberMonitor(sys.argv[1], sys.argv[2])
	if len(sys.argv)==4:
		subMonitor = SubscriberMonitor(sys.argv[1], sys.argv[2], ip=sys.argv[3])
	if len(sys.argv)==5:
		subMonitor = SubscriberMonitor(sys.argv[1], sys.argv[2], ip=sys.argv[3], port=sys.argv[4])
	subMonitor.setDaemon(False)
	subMonitor.start()

if __name__ == '__main__':
	sys.exit(main())
