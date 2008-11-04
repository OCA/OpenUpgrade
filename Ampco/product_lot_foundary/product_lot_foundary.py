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
import tools
import ir
import pooler


class stock_production_lot(osv.osv):
    _name = 'stock.production.lot'
    _inherit ='stock.production.lot'

    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product'),
        'heatcode_id' : fields.many2one('product.heatcode','HeatCode',ondelete='cascade',required=True,select=True),
        'quality' : fields.char('Quality Information',size=256),
        'localisation' : fields.char('Localisation',size=256),
#        'reservations'
#        'avilable'
    }

stock_production_lot()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

