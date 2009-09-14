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
    _name = "dm.address.segmentation"
    _description = "Segmentation"

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=32, required=True),
        'notes' : fields.text('Description'),
        'sql_query' : fields.text('SQL Query'),
        'customer_text_criteria_ids' : fields.one2many('dm.customer.text_criteria', 'segmentation_id', 'Customers Textual Criteria'),
        'customer_numeric_criteria_ids' : fields.one2many('dm.customer.numeric_criteria', 'segmentation_id', 'Customers Numeric Criteria'),
        'customer_boolean_criteria_ids' : fields.one2many('dm.customer.boolean_criteria', 'segmentation_id', 'Customers Boolean Criteria'),
        'customer_date_criteria_ids' : fields.one2many('dm.customer.date_criteria', 'segmentation_id', 'Customers Date Criteria'),
    }

    def set_customer_criteria(self, cr, uid, id, context={}):
        criteria=[]
        browse_id = self.browse(cr, uid, id)
        if browse_id.customer_text_criteria_ids:
            for i in browse_id.customer_text_criteria_ids:
                criteria.append("p.%s %s '%s'"%(i.field_id.name, i.operator, "%"+i.value+"%"))
        if browse_id.customer_numeric_criteria_ids:
            for i in browse_id.customer_numeric_criteria_ids:
                criteria.append("p.%s %s %f"%(i.field_id.name, i.operator, i.value))
        if browse_id.customer_boolean_criteria_ids:
            for i in browse_id.customer_boolean_criteria_ids:
                criteria.append("p.%s %s %s"%(i.field_id.name, i.operator, i.value))
        if browse_id.customer_date_criteria_ids:
            for i in browse_id.customer_date_criteria_ids:
                criteria.append("p.%s %s '%s'"%(i.field_id.name, i.operator, i.value))

        if criteria:
            sql_query = ("""select distinct p.name \nfrom res_partner p, sale_order s\nwhere p.id = s.customer_id and %s\n""" % (' and '.join(criteria))).replace('isnot','is not')
        else:
            sql_query = """select distinct p.name \nfrom res_partner p, sale_order s\nwhere p.id = s.customer_id"""
        return super(dm_address_segmentation,self).write(cr, uid, id, {'sql_query':sql_query})

    def create(self,cr,uid,vals,context={}):
        id = super(dm_address_segmentation,self).create(cr,uid,vals,context)
        self.set_customer_criteria(cr, uid, id)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        id = super(dm_address_segmentation,self).write(cr, uid, ids, vals, context)
        for i in ids:
            self.set_customer_criteria(cr, uid, i)
        return id

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

class dm_customer_text_criteria(osv.osv): # {{{
    _name = "dm.customer.text_criteria"
    _description = "Customer Segmentation Textual Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','like','char')],
               context={'model':'res.partner'}),
        'operator' : fields.selection(TEXT_OPERATORS, 'Operator', size=32),
        'value' : fields.char('Value', size=128),
    }
dm_customer_text_criteria() # }}}

class dm_customer_numeric_criteria(osv.osv): # {{{
    _name = "dm.customer.numeric_criteria"
    _description = "Customer Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','in',['integer','float'])],
               context={'model':'res.partner'}),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32),
        'value' : fields.float('Value', digits=(16,2)),
    }
dm_customer_numeric_criteria() # }}}

class dm_customer_boolean_criteria(osv.osv): # {{{
    _name = "dm.customer.boolean_criteria"
    _description = "Customer Segmentation Boolean Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','like','boolean')],
               context={'model':'res.partner'}),
        'operator' : fields.selection(BOOL_OPERATORS, 'Operator', size=32),
        'value' : fields.selection([('true','True'),('false','False')],'Value'),
    }
dm_customer_boolean_criteria() # }}}

class dm_customer_date_criteria(osv.osv): # {{{
    _name = "dm.customer.date_criteria"
    _description = "Customer Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','in',['date','datetime'])],
               context={'model':'res.partner'}),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32),
        'value' : fields.date('Date'),
    }
dm_customer_date_criteria() # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: