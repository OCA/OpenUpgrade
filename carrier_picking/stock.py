# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'address_carrier_id': fields.many2one('res.partner.address', 'Carrier Address'),
        'carrier_name': fields.char('Carrier Info', size=64, help="Additional carrier information (vehicle's plate, ...)"),
    }

    def change_carrier(self, cr, uid, ids, address_carrier_id=False):
        v = {}
        if address_carrier_id:
            address_carrier = self.pool.get('res.partner.address').browse(cr,uid,address_carrier_id)
            #print address_carrier.partner_id.name, address_carrier.name, address_carrier.plate
            v['carrier_name'] = address_carrier.partner_id.name + " / " + address_carrier.name + (address_carrier.plate and " / " + address_carrier.plate or "")
        return {'value':v}

stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
