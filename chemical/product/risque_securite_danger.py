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


import datetime
import time
import netsvc
from osv import fields,osv
import ir

# Definition of classes to manage risks, and Safety Hazards

class product_risque(osv.osv):
	_description='Risques Produits'
	_name = 'product.risque'
	_columns = {
		'name' : fields.char('Risque', size=64, required=True),
		'libelle' : fields.char('libelle', size=256, required=True),
	}
	_order = 'name'
product_risque()


class product_securite(osv.osv):
	_description='Securite Produits'
	_name = 'product.securite'
	_columns = {
		'name' : fields.char('Security', size=64, required=True),
		'libelle' : fields.char('libelle', size=256, required=True),
	}
	_order = 'name'
product_securite()

class product_danger(osv.osv):
	_description='Dangers Product'
	_name = 'product.danger'
	_columns = {
		'name' : fields.char('Danger', size=64, required=True),
		'libelle' : fields.char('libelle', size=256, required=True),
	}
	_order = 'name'
product_danger()

#Added 3 fields many2many in class product.product

class product_product(osv.osv):
	_name = 'product.product'
	_inherit = 'product.product'
	_columns = {
		'risque_ids': fields.many2many('product.risque', 'product_risque_rel', 'product_id','risque_id','Risk products'),
		'securite_ids': fields.many2many('product.securite', 'product_securite_rel', 'product_id','securite_id','Security'),
		'danger_ids': fields.many2many('product.danger', 'product_danger_rel', 'product_id','danger_id','Dangers products'),
	}
product_product()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:




