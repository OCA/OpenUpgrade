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
    _description = "Google Event"

    _columns = {
        'google_event_id': fields.char('Google Event Id', size=128, readonly=True),
        'event_modify_date': fields.datetime('Google Modify Date', readonly=True, help='google event modify date'),
        'write_date': fields.datetime('Date Modified', readonly=True, help='tiny event modify date'),
        'create_date': fields.datetime('Date created', readonly=True, help='tiny event create date'),
        'repeat_status': fields.selection([('norepeat', 'Does not Repeat'), ('daily', 'Daily'), ('everyweekday', 'Every weekday(Mon-Fri)'), ('every_m_w_f', 'Every Mon-Wed-Fri'), ('every_t_t', 'Every Tue-Thu'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], 'Repeats', size=32, required=False, readonly=False, help="Repeated status in google"),
        'privacy': fields.selection([('default', 'Default'),('public', 'Public'), ('private', 'Private')], 'Privacy', readonly=True, size=32),
        'email': fields.char('Email', size=256, help="Enter email addresses separated by commas", readonly=True),
                }

    _defaults = {
        'repeat_status': lambda *a: 'norepeat',
        'privacy': lambda *a: 'public',
    }
event_event()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: