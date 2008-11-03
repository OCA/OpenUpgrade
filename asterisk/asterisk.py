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

