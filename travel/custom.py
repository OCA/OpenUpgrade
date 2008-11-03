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
from osv import osv, fields

class travel_hostel(osv.osv):
    _name = 'travel.hostel'
    _inherit = 'res.partner'
    _table = 'res_partner'
    _columns = {
        'rooms_id': fields.one2many('travel.room', 'hostel_id', 'Rooms'),
        'quality': fields.char('Quality', size=16),
    }
travel_hostel()

class travel_airport(osv.osv):
    _name = 'travel.airport'
    _columns = {
        'name': fields.char('Airport name', size=16),
        'city': fields.char('City', size=16),
        'country': fields.many2one('res.country', 'Country')
    }
travel_airport()

class travel_room(osv.osv):
    _name = 'travel.room'
    _inherit = 'product.product'
    _table = 'product_product'
    _columns = {
        'beds': fields.integer('Nbr of Beds'),
        'view': fields.selection([('sea','Sea'),('street','Street')], 'Room View'),
        'hostel_id': fields.many2one('travel.hostel', 'Hostel'),
    }
travel_room()
class travel_flight(osv.osv):
    _name = 'travel.flight'
    _inherit = 'product.product'
    _table = 'product_product'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'PArtner'),
        'date': fields.datetime('Departure Date'),
        'airport_from': fields.many2one('travel.airport', 'Airport Departure'),
        'airport_to': fields.many2one('travel.airport', 'Airport Arrival'),
    }
travel_flight()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

