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
import subprocess

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config

from telnet_backend import telnet_backend
from RegisterIMEI import RegisterIMEI
from SubscriberMonitor import SubscriberMonitor

log = logging.getLogger(__name__)

## helper functions ##

def connect_bsc(settings):
	bsc = telnet_backend(settings['bsc_ip'], settings['bsc_port'])
	bsc.connect()
	return bsc

def connect_sgsn(settings):
	sgsn = telnet_backend(settings['sgsn_ip'], settings['sgsn_port'])
	sgsn.connect()
	return sgsn

def db_execute(db, sql_string, params=None):
	if params==None:
		rs = db.execute(sql_string)
	else:
		rs = db.execute(sql_string, params)
	db.commit()
	return rs
	
def db_query(db, sql_string, params=None):
	rs = db_execute(db, sql_string, params)
	return rs.fetchall()
	
def get_subscribers(db):
        # lists all subscribers
        #sql_string = "select extension, name, created, imsi, tmsi, lac, authorized from subscriber order by extension"
	# lists subscribers that at one point have been authorized
	#sql_string = "select extension, name, created, imsi, tmsi, lac, authorized from subscriber where not updated=created order by extension"
	# lists subscribers optimized for demo purposes
	sql_string = "select extension, name, created, imsi, tmsi, lac, authorized from subscriber where not updated=created or updated>date('now','-1 day') order by extension"

	return db_query(db,sql_string)
	
def get_attached_subscribers(db):
	sql_string = "select extension from subscriber where lac>0"
	return db_query(db,sql_string)

def get_subscriber_detail(db, ext):
	sql_string = "select imei,equipment.name,equipmentWatch.updated,imsi from equipment,equipmentwatch,subscriber where equipmentwatch.equipment_id=equipment.id and subscriber.id=equipmentwatch.subscriber_id and extension=? order by equipmentwatch.updated desc"
	return db_query(db, sql_string, (ext, ))

def get_sms_senders(db):
    sql_string = "select sms.id,subscriber.extension,sms.created,sms.sent,sms.text from sms,subscriber where sms.sender_id=subscriber.id"
    return db_query(db, sql_string)

def get_sms_receivers(db):
    sql_string = "select sms.id,subscriber.extension from sms,subscriber where sms.receiver_id=subscriber.id"
    return db_query(db, sql_string)

def update_subscriber_auth(db, ext):
	sql_string = "update subscriber set authorized=abs(authorized-1),lac=0,expire_lu=null,tmsi=null where extension=?"
	db_execute(db, sql_string, (ext,))
	
def delete_sms(db, sms_id):
	sql_string = "delete from sms where id=?"
	db_execute(db, sql_string, (sms_id,))

def clear_sms(db):
	sql_string = "delete from sms where 1=1"
	db_execute(db, sql_string)

def update_imei_name(db, imei, name):
	sql_string = "update equipment set name=? where imei=?"
	db_execute(db, sql_string, (name,imei))
            
def update_imsi_name(db, imsi, name):
	sql_string = "update subscriber set name=? where imsi=?"
	db_execute(db, sql_string, (name,imsi))

## Server URLs ##

@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(self):
    return {}

@view_config(route_name='www_root', renderer='home.mako')
def www_root(self):
    return {}

@view_config(route_name='subscribers', renderer='subscribers.mako')
def subscriber_view(request):
    settings = request.registry.settings
    mcc_mnc = settings['mcc_mnc']
    subscribers = []
    result = get_subscribers(request.db)
    if len(result)>0:
	for row in result:
            index = str(row[3])[:5]
            if mcc_mnc.has_key(index):
                operator=mcc_mnc[index]
            else:
                if mcc_mnc.has_key(index[:3]+"01"):
                    operator = list(mcc_mnc[index[:3]+"01"])
                    operator[1] = ""
                else:
                    operator = None
	    subscribers.append(dict(ext=row[0], name=row[1], created=row[2], imsi=row[3], operator=operator, tmsi=row[4], lac=row[5], authorized=row[6]))
    return {'subscribers': subscribers}

@view_config(route_name='subscriber_detail', renderer='subscriber_detail.mako')
def subscriber_detail_view(request):
    settings = request.registry.settings
    subscriber = []
    mm = None
    try:
      ext = int(request.matchdict['extension'])
    except:
      return HTTPFound(request.route_path('subscribers'))
    result = get_subscriber_detail(request.db, ext)
    if len(result)>0:
      reg_imei=RegisterIMEI()
      for row in result:
        imei = str(row[0]).zfill(15)
        imei_checksum = reg_imei.calculate_luhn(imei)
        if imei_checksum>0:
            imei = imei[:-1]+str(imei_checksum)
	subscriber.append(dict(imei=imei,name=row[1],updated=row[2]))
        sgsn = connect_sgsn(settings)
        if sgsn.connected==True:
            mm = sgsn.get_mm_context(str(row[3]))
            sgsn.close()
    return {'extension': ext,'subscriber': subscriber, 'mm': mm}

@view_config(route_name='scripts', renderer='scripts.mako')
def scripts_view(request):
    settings = request.registry.settings
    p = subprocess.Popen(["/etc/init.d/lcr","status"],stdout=subprocess.PIPE)
    lcr,err = p.communicate()
    p.wait()
    p = subprocess.Popen(["/etc/init.d/asterisk","status"],stdout=subprocess.PIPE)
    asterisk,err = p.communicate()
    p.wait()
    p = subprocess.Popen(["/etc/init.d/openggsn","status"],stdout=subprocess.PIPE)
    ggsn,err = p.communicate()
    p.wait()
    p = subprocess.Popen(["/etc/init.d/osmocom-nitb","status"],stdout=subprocess.PIPE)
    nitb,err = p.communicate()
    p.wait()
    p = subprocess.Popen(["/etc/init.d/osmocom-sgsn","status"],stdout=subprocess.PIPE)
    sgsn,err = p.communicate()
    p.wait()
    subMonitor = settings['subMonitor']
    return {'service_status': dict(lcr=lcr, asterisk=asterisk, ggsn=ggsn, nitb=nitb, sgsn=sgsn, subMonitor=subMonitor.is_running())}

@view_config(route_name='sms', renderer='sms.mako')
def sms_view(request):
    sms = []
    sender = get_sms_senders(request.db)
    receiver = get_sms_receivers(request.db)
    if len(sender)>0 and len(sender)==len(receiver):
	for i in range(0,len(sender)):
	    if sender[i][0]==receiver[i][0]:
	      sms.append(dict(id=receiver[i][0], from_id=sender[i][1], to_id=receiver[i][1], sent=sender[i][2], delivered=sender[i][3], message=sender[i][4]))
    return {'sms': sms}
    
@view_config(route_name='bsc', renderer='bsc.mako')
def bsc_view(request):
    settings = request.registry.settings
    bsc_version=None
    bsc_network=None
    bsc_statistics=None
    bsc = connect_bsc(settings)
    if bsc.connected:
	bsc_version = bsc.get_version()
	bsc_network = bsc.get_network_info()
        print bsc_network
	bsc_statistics = bsc.get_network_statistics()
	bsc.close()
    return {'bsc_version': bsc_version, 'bsc_network': bsc_network, 'bsc_statistics': bsc_statistics}

@view_config(route_name='sgsn', renderer='sgsn.mako')
def sgsn_view(request):
    settings = request.registry.settings
    sgsn_version=None
    ns_statistics=None
    sgsn = connect_sgsn(settings)
    if sgsn.connected:
        sgsn_version = sgsn.get_version()
        ns_statistics = sgsn.get_ns_stats()
        sgsn.close()
    return {'sgsn_version': sgsn_version, 'ns_statistics': ns_statistics}
    
@view_config(route_name='bts', renderer='bts.mako')
def bts_view(request):
    settings = request.registry.settings
    bts = collections.defaultdict()
    phys_cfg = ["NONE","CCCH","CCCH+SDCCH4","TCH/F","TCH/H","SDCCH8","PDCH","TCH/F_PDCH"]
    sgsn = connect_sgsn(settings)
    bssgp = None
    if sgsn.connected:
        bssgp = sgsn.get_bssgp_stats()
    bsc = connect_bsc(settings)
    if bsc.connected:
        bsc_network = bsc.get_network_info()
	helper = str(bsc_network[0]).find("has")
        num = int(str(bsc_network[0])[helper+4:].split()[0])
        for i in range(0,num):
            bts[i] = collections.defaultdict()
            bts[i]['timeslots'] = collections.defaultdict()
            bts[i]['stats'] = bsc.get_bts_info(str(i))
            bts[i]['description'] = bts[i]['stats'][1].split(": ")[1].strip()
            for j in range(0,8):
                helper = bsc.get_timeslot_info(str(i), str(j))
                bts[i]['timeslots'][j] = helper[0].replace("cfg","cfg:") + "," + helper[1]
                bts[i]['timeslots'][j] = bts[i]['timeslots'][j].split(",")[3:]
            if not bssgp==None:
                cid = str(bts[i]['stats'][0][bts[i]['stats'][0].find("has CI ")+7])
                if bssgp.has_key(cid):
                        bts[i]['bssgp'] = bssgp[cid]
                        nsei = str(bts[i]['bssgp'][0].split(",")[0].split()[1])
                        bts[i]['nsei'] = sgsn.get_nsei_info(nsei)
                        bts_tcp = bts[i]['nsei'][0].split()
                        bts[i]['ip'], bts[i]['port'] = bts_tcp[len(bts_tcp)-1].split(":")
        bsc.close()
    if sgsn.connected:
        sgsn.close()
    return {'bts': bts, 'phys_cfg': phys_cfg}

## Server Redirects ##

@view_config(route_name='delete_sms')
def delete_sms_view(request):
    try:
      sms_id = request.matchdict['id']
    except:
      return HTTPFound(request.route_path('sms'))
    delete_sms(request.db, sms_id)
    request.session.flash("SMS successfully deleted")
    return HTTPFound(request.route_path('sms'))

@view_config(route_name='clear_sms')
def clear_sms_view(request):
    clear_sms(request.db)
    request.session.flash("SMS Registry Cleared!")
    return HTTPFound(request.route_path('sms'))

@view_config(route_name='send_sms')
def send_sms_view(request):
    try:
      ext = str(request.matchdict['extension'])
      text = str(request.GET.get('text'))
    except:
       HTTPFound(request.route_path('subscribers'))
    settings = request.registry.settings
    bsc = connect_bsc(settings)
    if bsc.connected:
        bsc.send_sms(ext, ext, text)
        request.session.flash("SMS sent!")
        bsc.close()
    return HTTPFound(request.route_path('subscriber_detail',extension=ext))

@view_config(route_name='broadcast_sms')
def broadcast_sms_view(request):
    settings = request.registry.settings
    try:
       text = str(request.GET.get('text'))
    except:
       return HTTPFound(request.route_path('sms'))
    if len(text)>0:
       result = get_attached_subscribers(request.db)
       if len(result)>0:
           bsc = connect_bsc(settings)
           if bsc.connected:
               for ext in result:
                   bsc.send_sms(ext[0], ext[0], text)
               bsc.close()
               request.session.flash("Broadcast SMS sent!")
       else:
           request.session.flash("Broadcast SMS NOT SENT! No active subscribers!")
    return HTTPFound(request.route_path('sms'))

@view_config(route_name='manage_service')
def manage_service_view(request):
    settings = request.registry.settings
    try:
        service = request.matchdict['service']
        action = int(request.matchdict['action'])
    except:
        return HTTPFound(request.route_path('scripts'))
    if service=="lcr" or service=="asterisk" or service=="ggsn" or service=="nitb" or service=="sgsn":
        if service=="ggsn":
            service = "openggsn"
        if service=="nitb" or service=="sgsn":
            service = "osmocom-" + service
        if action==1:
            subprocess.call(["/etc/init.d/"+service,"start"])
        if action==2:
            subprocess.call(["/etc/init.d/"+service,"restart"])
        if action==3:
            subprocess.call(["/etc/init.d/"+service,"stop"])
    else:
        if service=="subMonitor":
            subMonitor = settings['subMonitor']
            if action==1 and not subMonitor.is_running():
                subMonitor.restart()
            if action==2:
                subMonitor.restart()
            if action==3 and subMonitor.is_running():
                subMonitor.stop()
    return HTTPFound(request.route_path('scripts'))

## AJAX views ##

@view_config(route_name='authorize_toggle', renderer='json')
def authorize_toggle(request):
    try:
        ext = int(request.matchdict['extension'])
    except:
        return {'success':0}
    update_subscriber_auth(request.db, ext)
    return {'success':1}

@view_config(route_name='authorize_imei', renderer='json')
def authorize_imei(request):
    settings = request.registry.settings
    try:
        imei = int(request.matchdict['imei'])
	imei = str(imei).zfill(15)
    except:
	return {'success':0}
    reg_imei = RegisterIMEI(settings['db'], imei)
    if reg_imei.pre_checks()<0:
        return {'success': reg_imei.pre_checks()}
    reg_imei.setDaemon(True)
    reg_imei.start()
    return {'success':1}

@view_config(route_name='clear_component', renderer='json')
def clear_component_view(request):
    try:
        field = str(request.matchdict['field'])
        reference = str(request.matchdict['reference'])
    except:
        return {'success':0}
    return HTTPFound(request.route_path('rename_component',field=field,reference=reference,value="clear"))

@view_config(route_name='rename_component', renderer='json')
def rename_component_view(request):
    try:
        field = str(request.matchdict['field'])
        reference = str(request.matchdict['reference'])
        value = str(request.matchdict['value'])
    except:
        return {'success':0}
    if(value=="clear"):
        value=""
    if(field=="imei" or field=="imsi"):
        if(field=="imei"):
            update_imei_name(request.db, reference, value)
        if(field=="imsi"):
            update_imsi_name(request.db, reference, value)
    else:
       return {'success':0}
    return {'success':1}
    
@view_config(route_name='toggle_channel',renderer='json')
def bts_channel_view(request):
    try:
        bts_id = str(request.matchdict['bts_id'])
        channel = str(request.matchdict['channel'])
        config = str(request.GET.get('config'))
    except:
        return {'success': 0}
    settings = request.registry.settings
    bsc = connect_bsc(settings)
    if bsc.connected and not config=="None":
        bsc.configure_timeslot(bts_id, channel, config)
        bsc.close()
    else:
        return {'success': 0}
    return {'success': 1}
    
