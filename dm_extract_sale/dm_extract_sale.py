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

import time
from osv import fields
from osv import osv
import pooler
import sys
import datetime
import netsvc

class dm_address_segmentation(osv.osv): # {{{
    
    _inherit = "dm.address.segmentation"
    _description = "Order Segmentation"

    _columns = {
        'order_text_criteria_ids' : fields.one2many('dm.extract.sale.text_criteria', 'segmentation_id', 'Customers Order Textual Criteria'),
        'order_numeric_criteria_ids' : fields.one2many('dm.extract.sale.numeric_criteria', 'segmentation_id', 'Customers Order Numeric Criteria'),
        'order_boolean_criteria_ids' : fields.one2many('dm.extract.sale.boolean_criteria', 'segmentation_id', 'Customers Order Boolean Criteria'),
        'order_date_criteria_ids' : fields.one2many('dm.extract.sale.date_criteria', 'segmentation_id', 'Customers Order Date Criteria'),
    }

    def set_address_criteria(self, cr, uid, id, context={}):
        sql_query = super(dm_address_segmentation,self).set_address_criteria(cr, uid, id, context)
        print "=========================================",sql_query
        sql_query.replace('from','from sale_order s, ')
        return sql_query


dm_address_segmentation() # }}}

TEXT_OPERATORS = [ # {{{
    ('like','like'),
    ('ilike','ilike'),
] # }}}

NUMERIC_OPERATORS = [ # {{{
    ('=','equals'),
    ('<','smaller then'),
    ('>','bigger then'),
] # }}}

BOOL_OPERATORS = [ # {{{
    ('is','is'),
    ('isnot','is not'),
] # }}}

DATE_OPERATORS = [ # {{{
    ('=','equals'),
    ('<','before'),
    ('>','after'),
] # }}}


class dm_extract_sale_text_criteria(osv.osv): # {{{
    _name = "dm.extract.sale.text_criteria"
    _description = "Customer Order Segmentation Textual Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','sale.order'),
               ('ttype','like','char')],
               context={'model':'sale.order'}, required = True),
        'operator' : fields.selection(TEXT_OPERATORS, 'Operator', size=32, required = True),
        'value' : fields.char('Value', size=128, required = True),
    }
dm_extract_sale_text_criteria() # }}}

class dm_extract_sale_numeric_criteria(osv.osv): # {{{
    _name = "dm.extract.sale.numeric_criteria"
    _description = "Customer Order Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','sale.order'),
               ('ttype','in',['integer','float'])],
               context={'model':'sale.order'}, required = True),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32, required = True),
        'value' : fields.float('Value', digits=(16,2), required = True),
    }
dm_extract_sale_numeric_criteria() # }}}

class dm_extract_sale_boolean_criteria(osv.osv): # {{{
    _name = "dm.extract.sale.boolean_criteria"
    _description = "Customer Order Segmentation Boolean Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','sale.order'),
               ('ttype','like','boolean')],
               context={'model':'sale.order'}, required = True),
        'operator' : fields.selection(BOOL_OPERATORS, 'Operator', size=32, required = True),
        'value' : fields.selection([('true','True'),('false','False')],'Value', required = True),
    }
dm_extract_sale_boolean_criteria() # }}}

class dm_extract_sale_date_criteria(osv.osv): # {{{
    _name = "dm.extract.sale.date_criteria"
    _description = "Customer Order Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','sale.order'),
               ('ttype','in',['date','datetime'])],
               context={'model':'sale.order'}, required = True),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32, required = True),
        'value' : fields.date('Date', required = True),
    }
dm_extract_sale_date_criteria() # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
