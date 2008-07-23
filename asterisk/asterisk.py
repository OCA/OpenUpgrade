# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: product_expiry.py 2103 2006-01-11 21:01:14Z pinky $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv

class asterisk_server(osv.osv):
    _name = 'asterisk.server'
    _columns = {
        'name' : fields.char('Asterisk Server', size=64, required=True),
        'host' : fields.char('Server Host', size=32, required=True),
        'port' : fields.integer('Server Port', required=True),
        'login' : fields.char('Login', size=32),
        'password' : fields.char('Password', size=32),
    }
    _defaults = {
        'host': lambda *args: 'localhost',
        'port': lambda *args: 807
    }
    _sql_constraint = [
        ('name_uniq', 'unique (name)', 'The Asterisk Server already exists !')
    ]
asterisk_server()

class asterisk_phone(osv.osv):
    _name = "asterisk.phone"
    _description = "IP Phone"
    _columns = {
        'name' : fields.char('Phone Name', size=64, required=True),
        'current_callerid' : fields.char('Current Caller', size=64),
        'ip' : fields.char('Phone IP', size=64),
        'phoneid' : fields.char('Phone ID', size=64),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'asterisk_id': fields.many2one('asterisk.server', 'Asterisk Server', required=True),
        'state': fields.selection([('connect','Connected'),('unconnected','Not Connected')], 'State')
    }
    _defaults = {
        'user_id': lambda s,cr,u,c: u,
        'state': lambda *args: 'connect'
    }
asterisk_phone()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

