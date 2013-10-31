# -*- coding: utf-8 -*-

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

import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound
import sqlite3, logging

from . import load_settings
log = logging.getLogger(__name__)

class Tester(unittest.TestCase):

	def setUp(self):
		self.settings = load_settings()
		self.config = testing.setUp()
		self.config.add_route('subscribers', '/subscribers/')

	def tearDown(self):
		testing.tearDown()
		self.settings['subMonitor'].stop()

	def generate_request(self):
		request = testing.DummyRequest()
		request.registry.settings = self.settings
		try:
			db = sqlite3.connect(self.settings['db'])
		except:
			log.debug('HLR database not found. Loading dummy database to memory')
			db = sqlite3.connect(":memory:")
		request.db = db
		return request

	### Properly importing additional modules for unit testings ###
	
	def _getClass_telnet_backend(self):
		from telnet_backend import telnet_backend
		return telnet_backend

	def _getClass_RegisterIMEI(self):
		from RegisterIMEI import RegisterIMEI
		return RegisterIMEI
		
	def _getClass_SubscriberMonitor(self):
		from SubscriberMonitor import SubscriberMonitor
		return SubscriberMonitor
	
	### telnet_backend unit tests ###
	
	def _test_telnet_connection(self, service):
		telnet_backend = self._getClass_telnet_backend()
		db = telnet_backend(self.settings[service+'_ip'], self.settings[service+'_port'])
		if db.connect():
			version = db.get_version()
			db.close()
			assert isinstance(version, list)
		else:
			assert isinstance(db, telnet_backend)

	def test_telnet_bsc_connection(self):
		self._test_telnet_connection("bsc")

	def test_telnet_sgsn_connection(self):
		self._test_telnet_connection("sgsn")

	### RegisterIMEI unit tests ###
	
	def test_RegisterIMEI(self):
		RegisterIMEI = self._getClass_RegisterIMEI()
		IMEI = "12345678901234"
		reg_imei = RegisterIMEI(imei=IMEI)
		self.assertEquals(reg_imei.pre_checks(),-1)
		luhn = reg_imei.calculate_luhn(IMEI)
		reg_imei.imei = IMEI + str((luhn+1)%10)
		self.assertEquals(reg_imei.pre_checks(),-2)
		reg_imei.imei = IMEI + str(luhn)
		self.assertEquals(reg_imei.pre_checks(),0)
		self.assertTrue(reg_imei.isvalid_imei(reg_imei.imei))
		
	### SubscriberMonitor unit tests ###
	
	def test_SubscriberMonitor(self):
		SubscriberMonitor = self._getClass_SubscriberMonitor()
		subMonitor = None
		try:
			subMonitor = SubscriberMonitor(self.settings['provider'], self.settings['db'], port=self.settings['bsc_port'])
		except:
			return
		assert isinstance(subMonitor, SubscriberMonitor)
		subMonitor.start()
		self.assertTrue(subMonitor.is_running)
		if subMonitor.is_running():
			subMonitor.stop()
			self.assertFalse(subMonitor.is_running())

	### server html view unit tests ###
	"""
		@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
		@view_config(route_name='www_root', renderer='home.mako')
		@view_config(route_name='subscribers', renderer='subscribers.mako')
		@view_config(route_name='subscriber_detail', renderer='subscriber_detail.mako')
		@view_config(route_name='scripts', renderer='scripts.mako')
		@view_config(route_name='sms', renderer='sms.mako')
		@view_config(route_name='bsc', renderer='bsc.mako')
		@view_config(route_name='sgsn', renderer='sgsn.mako')
		@view_config(route_name='bts', renderer='bts.mako')
	"""
	# testing to make sure that the web page generation does not crash
	
	def test_not_found(self):
		from .views import notfound_view
		result = notfound_view(self.generate_request())
		self.assertEqual(result, {})
	
	def test_www_root(self):
		from .views import www_root
		result = www_root(self.generate_request())
		self.assertEqual(result, {})
	
	def test_subscriber_view(self):
		from .views import subscriber_view
		result = subscriber_view(self.generate_request())
		self.assertTrue(result.has_key('subscribers'))
		
	def test_subscriber_detail_view(self):
		from .views import subscriber_view, subscriber_detail_view
		result = subscriber_detail_view(self.generate_request())
		if not isinstance(result,HTTPFound):
			self.assertTrue(result.has_key('extension')
				and result.has_key('subscriber')
				and result.has_key('mm'))
		else:
			log.debug(result)
		
	def test_scripts_view(self):
		from .views import scripts_view
		result = scripts_view(self.generate_request())
		self.assertTrue(result.has_key('service_status'))
		scripts = result['service_status']
		self.assertTrue(scripts.has_key('lcr')
			and scripts.has_key('asterisk')
			and scripts.has_key('ggsn')
			and scripts.has_key('nitb')
			and scripts.has_key('sgsn')
			and scripts.has_key('subMonitor'))
		
	def test_sms_view(self):
		from .views import sms_view
		result = sms_view(self.generate_request())
		self.assertTrue(result.has_key('sms'))
		
	def test_bsc_view(self):
		from .views import bsc_view
		result = bsc_view(self.generate_request())
		self.assertTrue(result.has_key('bsc_version')
			and result.has_key('bsc_network')
			and result.has_key('bsc_statistics'))
		
	def test_sgsn_view(self):
		from .views import sgsn_view
		result = sgsn_view(self.generate_request())
		self.assertTrue(result.has_key('sgsn_version')
			and result.has_key('ns_statistics'))
		
	def test_bts_view(self):
		from .views import bts_view
		result = bts_view(self.generate_request())
		self.assertTrue(result.has_key('bts')
			and result.has_key('phys_cfg'))
	
	### server URI command unit tests ###
	"""
		@view_config(route_name='delete_sms')
		@view_config(route_name='clear_sms')
		@view_config(route_name='send_sms')
		@view_config(route_name='broadcast_sms')
		@view_config(route_name='manage_service')
	"""
	# nothing to test here since these are all redirects
	
	### server ajax unit tests ###
	"""
		@view_config(route_name='authorize_toggle', renderer='json')
		@view_config(route_name='authorize_imei', renderer='json')
		@view_config(route_name='clear_component', renderer='json')
		@view_config(route_name='rename_component', renderer='json')
		@view_config(route_name='toggle_channel',renderer='json')
	"""
	# nothing to test here since these only say if the interaction with the database was successfull
	
