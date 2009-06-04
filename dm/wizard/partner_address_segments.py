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
import wizard
import pooler
from osv import fields
from osv import osv

segment_form = """<?xml version="1.0" ?>
<form string="Segments">
    <separator string="Segments" colspan="4"/>
    <field name="segment_ids" readonly="1" nolabel="1" colspan="4"/>
</form>"""

segment_fields = {
    'segment_ids':{'string':'Segments', 'type':'many2many', 'relation':'dm.campaign.proposition.segment'},
}

def _show_segments(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    wi_obj = pool.get('dm.workitem')
    workitems = wi_obj.search(cr,uid,[('address_id','=',data['id'])])
    data['form']['segment_ids'] = [wi.segment_id.id for wi in wi_obj.browse(cr,uid,workitems)]
    return data['form']

class wizard_address_segments(wizard.interface):
    states = {
        'init':{
            'actions': [_show_segments],
            'result': {'type':'form', 'arch':segment_form, 'fields':segment_fields, 'state':[('end', 'OK')]},
        },
    }
wizard_address_segments("wizard_address_segments")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: