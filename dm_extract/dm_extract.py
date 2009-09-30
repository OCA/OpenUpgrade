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
        'address_text_criteria_ids' : fields.one2many('dm.address.text_criteria', 'segmentation_id', 'Address Textual Criteria'),
        'address_numeric_criteria_ids' : fields.one2many('dm.address.numeric_criteria', 'segmentation_id', 'Address Numeric Criteria'),
        'address_boolean_criteria_ids' : fields.one2many('dm.address.boolean_criteria', 'segmentation_id', 'Address Boolean Criteria'),
        'address_date_criteria_ids' : fields.one2many('dm.address.date_criteria', 'segmentation_id', 'Address Date Criteria'),
    }

    def set_address_criteria(self, cr, uid, id, context={}):
        criteria=[]
        browse_id = self.browse(cr, uid, id)
        if browse_id.address_text_criteria_ids:
            for i in browse_id.address_text_criteria_ids:
                criteria.append("pa.%s %s '%s'"%(i.field_id.name, i.operator, "%"+i.value+"%"))
        if browse_id.address_numeric_criteria_ids:
            for i in browse_id.address_numeric_criteria_ids:
                criteria.append("pa.%s %s %f"%(i.field_id.name, i.operator, i.value))
        if browse_id.address_boolean_criteria_ids:
            for i in browse_id.address_boolean_criteria_ids:
                criteria.append("pa.%s %s %s"%(i.field_id.name, i.operator, i.value))
        if browse_id.address_date_criteria_ids:
            for i in browse_id.address_date_criteria_ids:
                criteria.append("pa.%s %s '%s'"%(i.field_id.name, i.operator, i.value))

        if criteria:
            sql_query = ("""select distinct pa.name \nfrom res_partner_address pa \nwhere %s\n""" % (' and '.join(criteria))).replace('isnot','is not')
        else:
            sql_query = """select distinct pa.name \nfrom res_partner_address pa """
        return sql_query

    def create(self,cr,uid,vals,context={}):
        id = super(dm_address_segmentation,self).create(cr,uid,vals,context)
        sql_query = self.set_address_criteria(cr, uid, id)
        self.write(cr, uid, id, {'sql_query':sql_query})
        return id

    def write(self, cr, uid, ids, vals, context=None):
        super(dm_address_segmentation,self).write(cr, uid, ids, vals, context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        for i in ids:
            sql_query = self.set_address_criteria(cr, uid, i)
            super(dm_address_segmentation,self).write(cr, uid, i, {'sql_query':sql_query})
        return ids

dm_address_segmentation() # }}}

class dm_campaign_proposition_segment(osv.osv):
    _name = "dm.campaign.proposition.segment"
    _description = "Segmentation"
    _inherit = "dm.campaign.proposition.segment"
    _columns = {
                'segmentation_id':fields.many2one('dm.address.segmentation','Segments'),
                }
    
dm_campaign_proposition_segment()

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

class dm_address_text_criteria(osv.osv): # {{{
    _name = "dm.address.text_criteria"
    _description = "address Segmentation Textual Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Address Field',
               domain=[('model_id.model','=','res.partner.address'),
               ('ttype','like','char')],
               context={'model':'res.partner.address'},required=True),
        'operator' : fields.selection(TEXT_OPERATORS, 'Operator', size=32 ,required=True),
        'value' : fields.char('Value', size=128,required=True),
    }
dm_address_text_criteria() # }}}

class dm_address_numeric_criteria(osv.osv): # {{{
    _name = "dm.address.numeric_criteria"
    _description = "address Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Address Field',
               domain=[('model_id.model','=','res.partner.address'),
               ('ttype','in',['integer','float'])],
               context={'model':'res.partner.address'},required=True),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32,required=True),
        'value' : fields.float('Value', digits=(16,2),required=True),
    }
dm_address_numeric_criteria() # }}}

class dm_address_boolean_criteria(osv.osv): # {{{
    _name = "dm.address.boolean_criteria"
    _description = "address Segmentation Boolean Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Address Field',
               domain=[('model_id.model','=','res.partner.address'),
               ('ttype','like','boolean')],
               context={'model':'res.partner.address'},required=True),
        'operator' : fields.selection(BOOL_OPERATORS, 'Operator', size=32,required=True),
        'value' : fields.selection([('true','True'),('false','False')],'Value',required=True),
    }
dm_address_boolean_criteria() # }}}

class dm_address_date_criteria(osv.osv): # {{{
    _name = "dm.address.date_criteria"
    _description = "address Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.address.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Address Field',
               domain=[('model_id.model','=','res.partner.address'),
               ('ttype','in',['date','datetime'])],
               context={'model':'res.partner.address'},required=True),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32,required=True),
        'value' : fields.date('Date',required=True),
    }
dm_address_date_criteria() # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
