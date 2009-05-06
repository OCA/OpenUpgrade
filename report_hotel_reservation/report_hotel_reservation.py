# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('confirm','Confirm'),
    ('done', 'Done')
 
]

class report_hotel_reservation_status(osv.osv):
    _name = "report.hotel.reservation.status"
    _description = "Reservation By State"
    _auto = False
    _columns = {
        
        'reservation_no':fields.char('Reservation No',size=64,readonly=True),
        'nbr': fields.integer('Reservation', readonly=True),
        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),
        
    }
    
    def init(self, cr):
        cr.execute("""
            create or replace view report_hotel_reservation_status as (
                select
                    min(c.id) as id,
                    c.reservation_no,
                    c.state,
                    count(*) as nbr
                from
                    hotel_reservation c
                group by c.state,c.reservation_no
            )""")
report_hotel_reservation_status()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
