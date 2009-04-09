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
import math
from osv import fields,osv
import tools
import ir
import pooler

class sale_agent(osv.osv):
	_name = "sale.agent"
        _description = "Sale agent sale info"
	_columns = {
			    'name': fields.char('Saleagent Name', size=25, required=True),
			    'partner_id': fields.many2one('res.partner','Partner',required=True,ondelete='cascade'),
			    'customer':fields.one2many('res.partner','agent_id','Customer'),
			    'comprice_id': fields.many2one('product.pricelist','commission price list',  required=True,ondelete='cascade'),
			    'active': fields.boolean('Active'),
	}
	_defaults = {
               	'active': lambda *a: True,
                }
sale_agent()

#
# En Sale_agent class
#
