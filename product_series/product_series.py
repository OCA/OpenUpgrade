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
class product_series(osv.osv):
	_name = "product.series"
	_description = "Partner Product Series"
	_columns = {
		'partner_id' : fields.many2one('res.partner','Manufacturer',required=True,select=True),
		'code': fields.char('Code', size=64, select=True),
		'name': fields.char('Name', size=64, select=True),
		'description': fields.char('Description', size=128, select=True),
	}


product_series()


class product_product(osv.osv):
	_inherit ="product.product"
	_name = "product.product"
	_columns = {
		'series': fields.many2one('product.series','Series'),
	}

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: