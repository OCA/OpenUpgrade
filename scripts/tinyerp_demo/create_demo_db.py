#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import xmlrpclib
import time
import base64

import sys

demo_profile = sys.argv[1]

def wrong_profile():
	print "Cannot find SaaS demo profile :",demo_profile
	sys.exit()

if demo_profile == 'service_fr':
	profile = 'profile_service'
	l10n_chart = 'l10n_be'
	lang = 'fr_FR'
	dbname = 'service_fr'
elif demo_profile == 'service_en':
	profile = 'profile_service'
	l10n_chart = 'l10n_chart_uk_minimal'
	lang = 'en_US'
	dbname = 'service_en'
elif demo_profile == 'manufacturing_fr':
	profile = 'profile_manufacturing'
	l10n_chart = 'l10n_be'
	lang = 'fr_FR'
	dbname = 'manufacturing_fr'
elif demo_profile == 'manufacturing_en':
	profile = 'profile_manufacturing'
	l10n_chart = 'l10n_chart_uk_minimal'
	lang = 'en_US'
	dbname = 'manufacturing_en'
elif demo_profile == 'accounting_fr':
	profile = 'profile_accounting'
	l10n_chart = 'l10n_be'
	lang = 'fr_FR'
	dbname = 'accounting_fr'
elif demo_profile == 'accounting_en':
	profile = 'profile_accounting'
	l10n_chart = 'l10n_chart_uk_minimal'
	lang = 'en_US'
	dbname = 'accounting_en'
elif demo_profile == 'auction_fr':
	profile = 'profile_auction'
	l10n_chart = 'l10n_be'
	lang = 'fr_FR'
	dbname = 'auction_fr'
elif demo_profile == 'auction_en':
	profile = 'profile_auction'
	l10n_chart = 'l10n_chart_uk_minimal'
	lang = 'en_US'
	dbname = 'auction_en'
else:
	wrong_profile()


url = 'http://localhost:8069/xmlrpc'

sock = xmlrpclib.ServerProxy(url+'/object')
sock2 = xmlrpclib.ServerProxy(url+'/db')
sock3 = xmlrpclib.ServerProxy(url+'/common')
sock4 = xmlrpclib.ServerProxy(url+'/wizard')

admin_passwd = 'admin'

def wait(id):
    progress=0.0
    while not progress==1.0:
        progress,users = sock2.get_progress(admin_passwd, id)
    return True

def drop_db():
    ok = False
    range = 4
    while (not ok) and range:
        try:
            time.sleep(4)
            id = sock2.drop(admin_passwd, dbname)
            ok = True
        except:
            range -= 1

    return ok

def create_db():
    id = sock2.create(admin_passwd, dbname, True, lang)
    wait(id)
    uid = sock3.login(dbname, 'admin', 'admin')

    idprof = sock.execute(dbname, uid, 'admin', 'ir.module.module', 'search', [('name','=',profile)])
    idl10n = sock.execute(dbname, uid, 'admin', 'ir.module.module', 'search', [('name','=',l10n_chart)])
    wiz_id = sock4.create(dbname, uid, 'admin', 'base_setup.base_setup')
    state = 'init'
    datas = {'form':{}}
    while state!='config':        
        res = sock4.execute(dbname, uid, 'admin', wiz_id, datas, state, {})
        if state=='init':
            datas['form'].update( res['datas'] )
        if res['type']=='form':
            for field in res['fields'].keys():               
                datas['form'][field] = datas['form'].get(field,False)
            state = res['state'][-1][0]
            datas['form'].update({
                'profile': idprof[0]                
            })
        elif res['type']=='state':
            state = res['state']

    res = sock4.execute(dbname, uid, 'admin', wiz_id, datas, state, {})

    return True

def load_languages(*langs):
    uid = sock3.login(dbname, 'admin','admin')

    wiz_id = sock4.create(dbname, uid, 'admin', 'module.lang.install')
    for lang in langs:
        ok = sock4.execute(dbname, uid, 'admin', 20, {'form': {'lang': lang}}, 'start', {})
        if not ok:
            return False

    return True

def load_demo_module():
    uid = sock3.login(dbname, 'admin','admin')
    ids = sock.execute(dbname, uid, 'admin', 'ir.module.module', 'search', [('name', '=', 'demo_setup')])
    if not ids:
        return False

    res = sock.execute(dbname, uid, 'admin', 'ir.module.module', 'button_install', ids, {})

    datas = {'model': 'ir.module.module', 
             'form': {'module_download': '', 
                      'module_info': 'demo_setup : to install'}, 
                      'id': ids[0], 
                      'report_type': 'pdf', 
                      'ids': ids}

    wiz_id = sock4.create(dbname, uid, 'admin', 'module.upgrade')
    sock4.execute(dbname, uid, 'admin', wiz_id, datas, 'init', {})

    wiz_id = sock4.create(dbname, uid, 'admin', 'module.upgrade')
    sock4.execute(dbname, uid, 'admin', wiz_id, datas, 'start', {})

    return True

print "Drop existing database '%s':" % (dbname),
sys.stdout.flush()

if drop_db():
    print "OK"
else:
    print "FAIL"


print "Creating new database '%s':" %(dbname),
sys.stdout.flush()

if create_db():
    print "OK"
else:
    print "FAIL"


#print "Loading demo module:",
#sys.stdout.flush()

#if load_demo_module():
#    print "OK"
#else:
#    print "FAIL"


#print "Loading additional languages:",
#sys.stdout.flush()

#if load_languages('fr_FR', 'en_US'):
#    print "OK"
#else:
#    print "FAIL"
