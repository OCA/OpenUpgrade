##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

import time
from osv import fields,osv
import pooler

class stock_heatcode(osv.osv):
	_name = 'product.lot.foundry.heatcode'
	_description = "Heat Code"
	_columns = {
		'name': fields.char('Heat Code', size=64, required=True),
		'date': fields.date('Date', required=True),
		'chemical_ids': fields.one2many('product.lot.foundry.heatcode.chemical', 'heatcode_id', 'Chemical Properties'),
		'mecanical_ids': fields.one2many('product.lot.foundry.heatcode.mecanical', 'heatcode_id','Mecanical Properties'),
		'lot_ids': fields.one2many('stock.production.lot', 'heatcode_id','Lots'),
		'state': fields.selection([
			('draft','Draft'),
			('valid','Valid')
		], 'State', required=True)
	}
	_defaults = {
		'date': lambda *args: time.strftime('%Y-%m-%d'),
		'state': lambda *args: 'draft'
	}
stock_heatcode()


class stock_heatcode_mecanical(osv.osv):
	_name = 'product.lot.foundry.heatcode.mecanical'
	_description = "Mecanical Properties"
	_columns = {
		'name': fields.char('Property', size=64, required=True),
		'value': fields.char('Value', size=64, required=True),
		'heatcode_id': fields.many2one('product.lot.foundry.heatcode', 'Heatcode'),
	}
stock_heatcode_mecanical()


class stock_heatcode_chemical(osv.osv):
	_name = 'product.lot.foundry.heatcode.chemical'
	_description = "Chemical Properties"
	_columns = {
		'name': fields.char('Property', size=64, required=True),
		'value': fields.char('Value', size=64, required=True),
		'heatcode_id': fields.many2one('product.lot.foundry.heatcode', 'Heatcode'),
	}
stock_heatcode_chemical()



class stock_production_lot(osv.osv):
	_name = 'stock.production.lot'
	_inherit = 'stock.production.lot'
	def _available_get(self, cr, uid, ids, name, args, context={}):
		res = {}
		for lot in self.browse(cr, uid, ids, context):
			if lot.type=='bar':
				x = lot.size_x
				for res in lot.reservation_ids:
					x -= res.size_x
				res[id] = '%.2f mm'% (x,)
			else:
				res[id] = '134mm x 122mm x 12mm\n134mm x 22mm x 12mm'
		return res
	_columns = {
		'name': fields.date('Date'),
		'size_x': fields.float('Width'),
		'size_y': fields.float('Length'),
		'size_z': fields.float('Height'),
		'heatcode_id': fields.many2one('product.lot.foundry.heatcode', 'Heatcode'),
		'type': fields.selection([
			('bar','Bar'),
			('plate','Plate')
		], 'Type', required=True),
		'status': fields.selection([
			('draft', 'Draft'),
			('valid', 'Valid'),
			('non conformity', 'Non Conformity'),
			('done', 'Done')
		], 'Status', required=True),
		'quality_info': fields.text('Quality Information'),
		'reservation_ids': fields.one2many('stock.production.lot.reservation', 'lot_id', 'Reservations'),
		'available': fields.function(_available_get, type="text", method=True, string='Availables'),
	}
	_defaults = {
		'status': lambda *args: 'draft',
		'name': lambda *args: time.strftime('%Y-%m-%d'),
		'type': lambda *args: 'bar'
	}
stock_production_lot()

class stock_production_lot_reservation(osv.osv):
	_name = 'stock.production.lot.reservation'
	_columns = {
		'name': fields.date('Date'),
		'size_x': fields.float('Width'),
		'size_y': fields.float('Length'),
		'size_z': fields.float('Height'),
		'lot_id': fields.many2one('stock.production.lot', 'Lot', required=True, ondelete="cascade")
	}
stock_production_lot_reservation()
