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

class airport_airport(osv.osv):
    _name = 'airport.airport'
    _columns = {
        'name': fields.char('Airport name', size=16),
        'city': fields.char('City', size=16),
        'country_id': fields.many2one('res.country', 'Country'),
        'lines': fields.many2many('airport.airport', 'airport_airport_lines_rel', 'source','destination', 'Flight lines')
    }
airport_airport()

class airport_flight(osv.osv):
    _name = 'airport.flight'
    _inherit = 'product.product'
    _table = 'product_product'
    _columns = {
        'date': fields.datetime('Departure Date'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'airport_from': fields.many2one('airport.airport', 'Airport Departure'),
        'airport_to': fields.many2one('airport.airport', 'Airport Arrival'),
    }
airport_flight()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

