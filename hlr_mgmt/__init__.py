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

import os, logging
import sqlite3
import collections, csv

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config

from SubscriberMonitor import SubscriberMonitor

log = logging.getLogger(__name__)
here = os.path.dirname(os.path.abspath(__file__))

## MC/MNC parsing ##

def parse_mcc_csv(csv_file):
    log.debug('Parsing MCC MNC csv file...')
    mcc_mnc = collections.defaultdict()
    csv_obj = open(csv_file)
    csv_reader = csv.reader(csv_obj, delimiter=',')
    #country
    #mcc, mnc, network, operator or brand name, status
    for row in csv_reader:
        if len(row)==1:
            country=row[0]
        else:
            index = row[0]+row[1]
            if len(row[3])>0:
                mcc_mnc[index] = (country,row[3])
            else:
                mcc_mnc[index] = (country,row[2])
    return mcc_mnc

def close_db_connection(request):
    request.db.close()

# Application Subscribers ( Event Listeners )
@subscriber(NewRequest)
def new_request_subscriber(event):
    request = event.request
    #log.debug('Received HTTP Request from ' + request.environ['REMOTE_ADDR'] + " for URI: " + request.environ['PATH_INFO'])
    settings = request.registry.settings
    request.db = sqlite3.connect(settings['db'])
    request.add_finished_callback(close_db_connection)

def load_settings():
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'templates')
    settings['mako.input_encoding'] = 'utf-8'
    
    # OpenBSC Settings
    settings['provider'] = '<<Provider Name>>'
    settings['db'] = '/etc/openbsc/hlr.sqlite3'
    settings['bsc_ip'] = "127.0.0.1"
    settings['sgsn_ip'] = "127.0.0.1"
    settings['bsc_port'] = 4242
    settings['sgsn_port'] = 4245
    
    # loads MCC MNC codes to memory
    mcc_mnc = os.path.join(here,'mcc_mnc.csv')
    settings['mcc_mnc'] = parse_mcc_csv(mcc_mnc)
    # mcc_mnc was obtained manually from http://mobile-network-codes.com/mobile-network-codes-country-codes.asp

    # initiates SubscriberMonitor
    subMonitor = SubscriberMonitor(settings['provider'], settings['db'], port=settings['bsc_port'])
    subMonitor.setDaemon(True)
    subMonitor.start()
    settings['subMonitor'] = subMonitor
    
    return settings

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings = load_settings
    
    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('0p3nb5c.5ign4tur3')
    
    # configuration setup
    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_debugtoolbar')
    config.include('pyramid_exclog')

    # routes setup
    config.add_route('www_root','/')
    config.add_route('bsc', '/bsc/')
    config.add_route('bts', '/bts/')
    config.add_route('toggle_channel', '/bts/{bts_id}/{channel}/')
    config.add_route('sgsn', '/sgsn/')
    config.add_route('subscribers', '/subscribers/')
    config.add_route('subscriber_detail','/subscribers/{extension}')
    config.add_route('authorize_imei','/authorize/imei/{imei}')
    config.add_route('authorize_toggle','/authorize/subscriber/{extension}')
    config.add_route('rename_component','/rename/{field}/{reference}/{value}')
    config.add_route('clear_component','/rename/{field}/{reference}/')
    config.add_route('sms', '/sms/')
    config.add_route('delete_sms','/sms/delete/{id}')
    config.add_route('clear_sms','/sms/clear')
    config.add_route('send_sms','/sms/single/{extension}/')
    config.add_route('broadcast_sms','/sms/broadcast/')
    config.add_route('scripts','/scripts/')
    config.add_route('manage_service','/scripts/manage_service/{service}/{action}')
    
    # static view setup
    config.add_static_view('static', os.path.join(here, 'static'))
    
    # scan for @view_config and @subscriber decorators
    config.scan()

    # serve app
    log.debug('Listening for HTTP requests...')
    return config.make_wsgi_app()
