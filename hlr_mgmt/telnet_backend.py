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

import telnetlib, logging, collections

log = logging.getLogger(__name__)

class telnet_backend(object):
	## Initialization and Settings ##
	
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.conn = None
		self.connected = False
		self.sms_limit = 160

	## Common Commands ##
	
	def connect(self):
		try:
			self.conn = telnetlib.Telnet(self.ip, self.port)
			self.conn.read_until("> ")
			self.conn.write("enable\n")
			self.conn.read_until("# ")
			self.connected = True
			return True
		except:
			return False

	def close(self):
		try:
			self.conn.write("exit")
			self.conn.close()
			self.connected = False
			return True
		except:
			return False

	def execute(self, cmd):
		try:
			self.conn.write(cmd+"\n")
			result = self.conn.read_until("# ")
			result = result[len(cmd)+1:-10]
			return self.sanitize_telnet(result)
		except:
			return None
	
	def save_config(self):
		try:
			self.execute('copy running-config startup-config')
			return True
		except:
			return False

        def sanitize_telnet(self, input):
                output = input.decode('utf_8')
		output = ' '.join(output.split(' '))
		return output.split("\r\n")

	def get_version(self):
		return self.execute("show version")

	## OpenBSC Commands ##
		
	def send_sms(self, src, dest, text):
		sms_cmd =  "subscriber extension " + str(dest) + " sms sender extension " + str(src) + " send "
		self.execute(sms_cmd + text[:self.sms_limit])

	def send_welcome_sms(self, provider, ext):
		log.debug("sending welcome message to Extension: " + str(ext))
		sms_string = "Welcome to " + provider + ". Your Local Number is " + str(ext) + "."
		self.send_sms(ext,ext,sms_string)
		sms_string = "To call other " + provider + " customers use their 5 digit extention. Otherwise, please dial the number normally."
		self.send_sms(ext,ext,sms_string)

	def configure_timeslot(self, bts, timeslot, config):
		self.execute('configure terminal')
		self.execute('network')
		self.execute('bts ' + bts)
		self.execute('trx 0')
		self.execute('timeslot ' + timeslot)
		self.execute('phys_chan_config ' + config)
		self.execute('end')
		return self.save_config()

	def get_network_info(self):
		return self.execute("show network")

	def get_network_statistics(self):
		return self.execute("show statistics")
	
	def get_bts_info(self, bts):
		return self.execute("show bts " + bts)

	def get_timeslot_info(self, bts, timeslot):
		return self.execute("show timeslot " + bts + " 0 " + timeslot)
		
	def set_bts_description(self, bts, description):
		self.execute('configure terminal')
		self.execute('network')
		self.execute('bts ' + bts)
		self.execute('description ' + description)
		return self.save_config()

	## OpenSGSN Commands ##	
	
	def get_mm_context(self, imsi):
		return self.execute('show mm-context imsi ' + imsi)
	
	def get_ns_stats(self):
		return self.execute('show ns stats')[:-1]

	def get_nsei_info(self,nsei):
		return self.execute('show ns nsei ' + nsei + ' stats')

	def get_bssgp_stats(self):
		bad_output =  self.execute('show bssgp stats')
		fixed_output = list()
		final_output = collections.defaultdict()
		for row in bad_output:
			if row.find("\n")<0:
				fixed_output.append(row)
			else:
				fixed_output.append(row.split("\n")[0])
				fixed_output.append(row.split("\n")[1])
		fixed_output[1:] = fixed_output[1:]
		active = False
		for row in range(0,len(fixed_output)):
			if fixed_output[row].find("NSEI")>=0:
				if not fixed_output[row][fixed_output[row].find("RA-ID: ")+7]=="0":
					CID =  str(fixed_output[row][fixed_output[row].find("CID: ")+5:fixed_output[row].rfind(",")])
					final_output[CID] = list()
					active = True
				else:
					active = False
			if active:
				final_output[CID].append(fixed_output[row])
		return final_output

