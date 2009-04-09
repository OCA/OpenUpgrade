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

import rpc
import xmlrpclib
import sys
import time

DB = 'terp5'
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % ('localhost',8069))


t = time.time()

#sock.execute('terp5', 1, 'a', 'ir.values', 'get', 'action', 'tree_but_open', [('ir.ui.menu', 111)], False, {'lang': u'en_US', 'tz': u'America/Aruba'})
#print time.time() - t
#sock.execute('terp5', 1, 'a', u'board.note', 'fields_view_get', False, u'form', {'lang': u'en_US', 'tz': u'America/Aruba', 'active_ids': [111], 'active_id': 111}, True)
#print time.time() - t
#sock.execute('terp5', 1, 'a', 'board.note', 'default_get', ['note', 'date', 'user_id', 'name', 'type'], {'lang': u'en_US', 'tz': u'America/Aruba', 'active_ids': [111], 'active_id': 111})
#print time.time() - t
#sock.execute('terp5', 1, 'a', 'res.users', 'name_get', [1], {'lang': u'en_US', 'tz': u'America/Aruba'})
#print time.time() - t
#
t = time.time()
sock2 = rpc.tiny_sock('socket://%s:%s' % ('localhost',8070), 'terp5', 1, 'a')
sock2.exec_auth('execute', 'ir.values', 'get', 'action', 'tree_but_open', [('ir.ui.menu', 111)], False, {'lang': u'en_US', 'tz': u'America/Aruba'})
print time.time() - t
sock2 = rpc.tiny_sock('socket://%s:%s' % ('localhost',8070), 'terp5', 1, 'a')
sock2.exec_auth('execute', u'sale.order', 'fields_view_get', False, u'form', {'lang': u'en_US', 'tz': u'America/Aruba', 'active_ids': [111], 'active_id': 111}, True)
print time.time() - t
sock2 = rpc.tiny_sock('socket://%s:%s' % ('localhost',8070), 'terp5', 1, 'a')
sock2.exec_auth('execute', 'sale.order', 'default_get', ['note', 'date', 'user_id', 'name', 'type'], {'lang': u'en_US', 'tz': u'America/Aruba', 'active_ids': [111], 'active_id': 111})
print time.time() - t

