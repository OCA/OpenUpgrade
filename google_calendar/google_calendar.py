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

from osv import fields, osv

class res_users(osv.osv):
    _inherit = "res.users"
    _description = 'res.users'

    _columns = {
        'google_email':fields.char('Google Email Id', size=128),
        'google_password': fields.char('Password', size=128),
                }
res_users()

class event_event(osv.osv):
    _inherit = "event.event"
    _description = "Event"

    _columns = {
        'google_event_id': fields.char('Google Event Id', size=128, readonly=True),
        'event_modify_date': fields.datetime('Google Modify Date', readonly=False),
        'write_date': fields.datetime('Date Modified', readonly=True),
        'create_date': fields.datetime('Date create', readonly=True),
                }
event_event()