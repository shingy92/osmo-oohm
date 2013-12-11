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
#from datetime import datetime, timedelta
#from multiprocessing import Process

log = logging.getLogger(__name__)

class RegisterIMEI(threading.Thread):
	## Initialization and Settings ##
	
	def __init__(self, db=None, imei=None):
		threading.Thread.__init__(self)
		self.HLR_DB = db
		self.imei = imei

	## Luhn checksum functions courtesy of Wikipedia ##

	def digits_of(self,n):
		return [int(d) for d in str(n)]

	def luhn_checksum(self,imei):
		digits = self.digits_of(imei)
		odd_digits = digits[-1::-2]
		even_digits = digits[-2::-2]
		checksum = 0
		checksum += sum(odd_digits)
		for d in even_digits:
			checksum += sum(self.digits_of(d*2))
		return checksum % 10
	 
	def calculate_luhn(self,imei_zero):
		if not len(self.digits_of(imei_zero)) == 14:
			if len(self.digits_of(imei_zero)) == 15:
				imei_zero = imei_zero[:14]
			else:
				return -1
		check_digit = self.luhn_checksum(int(imei_zero) * 10)
		return check_digit if check_digit == 0 else 10 - check_digit

	 ## Class Functions ##
	 
	def isvalid_imei(self,imei):
		return self.luhn_checksum(imei) == 0
	
	def get_imsi(self,imei):
		sql_imei = (imei,)
		# gets the imei-imsi mapping registered in the last hour
		sql_string="select subscriber.imsi from equipment,equipmentwatch,subscriber where equipmentwatch.equipment_id=equipment.id and subscriber.id=equipmentwatch.subscriber_id and equipment.updated=equipmentwatch.updated and equipment.updated>=datetime('now','-1 hour') and imei=?"
		self.cursor.execute(sql_string,sql_imei)
		return self.cursor.fetchall()
	
	def authorize_subscriber(self,imsi):
		sql_imsi = (str(imsi[0]),)
		sql_string="update subscriber set authorized=1 where imsi=?"
		self.cursor.execute(sql_string,sql_imsi)
		self.sqlconn.commit()
		self.sqlconn.close()

	def pre_checks(self):
		if not len(self.digits_of(self.imei)) == 15:
                        log.debug("IMEI: " + self.imei + " has incorrect length")
                        return -1
                if not self.isvalid_imei(self.imei):
                        log.debug("IMEI: " + self.imei + " has incorrect checksum digit")
                        return -2
		return 0
			
	def authorize_imei(self,imei):
		precheck = self.pre_checks()
		if precheck<0:
			return precheck
		
		#replaces checksum digit with zero to be consistent with how OpenBSC stores the IMEI values
		#imei = imei/10*10
		imei = imei[:-1] + '0'
		imsi = self.get_imsi(imei)
		
		# loop that guarantees we get the latest imei-imsi mapping to avoid accidentally registering a SIM card no longer present in the phone
		tries = 1
		while len(imsi)==0 and tries <= 60:
			log.debug("IMEI: " + imei + " not found, trying again in 1 minute...")
			time.sleep(60)
			imsi = self.get_imsi(imei)
			tries = tries + 1

		if len(imsi)==0:
			log.debug("waiting period over for IMEI: " + imei + "...")
			return -3
		else:
			log.debug("Authorizing IMSI found in IMEI: " + imei)
			self.authorize_subscriber(imsi[0])
			return 0

	def run(self):
		log.debug("starting RegisterIMEI deamon")
		self.sqlconn = sqlite3.connect(self.HLR_DB,60)
		self.cursor = self.sqlconn.cursor()
		return self.authorize_imei(self.imei)

def main():
	if len(sys.argv)<3:
		print "ERROR: not enough arguments\n"
		print "USAGE: python " + sys.argv[0] + " /path/to/hlr_db.sqlite3 imei\n"
		exit(1)
	reg_imei = RegisterIMEI(sys.argv[1],sys.argv[2])
	reg_imei.setDaemon(True)
	reg_imei.start()

if __name__ == '__main__':
	sys.exit(main())
