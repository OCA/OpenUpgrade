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
import time

from osv import fields
from osv import osv
import pooler

class dm_document_template(osv.osv):
    _name = "dm.document.template"
    _columns = {
        'name' : fields.char('Tempalte Name', size=128),
        'dynamic_fields' : fields.many2many('ir.model.fields','dm_tempalte_fields','template_field_id','tempalte_id','Fields',domain=[('model','like','dm.%')]),
        }
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_document_template,self).write(cr, uid, ids, vals, context)
        document_template =self.read(cr,uid,ids)[0]
        list1 = document_template['dynamic_fields']
        dm_offer_document = self.pool.get('dm.offer.document')
        document_ids = dm_offer_document.search(cr,uid,[('document_template_id','=',ids[0])])
        documents = dm_offer_document.read(cr,uid,document_ids)
        for doc in documents:
            list2 = doc['document_template_field_ids'] 
            diff = list(set(list2).difference(set(list1)))
            map(lambda x : list2.remove(x) ,diff)
            dm_offer_document.write(cr,uid,doc['id'],{'document_template_field_ids':[[6, 0,list2]]})
        return res                 
dm_document_template()