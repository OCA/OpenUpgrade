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
<form string="Duplication Of Proposition">
    <field name="keep_segments"/>
</form>"""

segment_fields = {
    'keep_segments':{'string':'Keep Segments At Duplication', 'type':'boolean','default': lambda *a:True},
}

def _copy_prp(self, cr, uid, data, context):
    prop_id = data['id']
    pool = pooler.get_pool(cr.dbname)
    prp_id = pool.get('dm.campaign.proposition').copy(cr, uid, prop_id, context=context)
    datas = pool.get('dm.campaign.proposition').browse(cr, uid, prp_id, context)
    seg = data['form']['keep_segments']
    if datas.segment_ids:
        if not seg:
            l = []
            for i in datas.segment_ids:
                l.append(i.id)
                pool.get('dm.campaign.proposition.segment').unlink(cr,uid,l)
            return {'PRP_ID':prp_id}
    return {'PRP_ID':prp_id}

class wizard_prop_copy(wizard.interface):
    states = {
        'init':{
            'actions': [],
            'result': {'type':'form', 'arch':segment_form, 'fields':segment_fields, 'state': [('end', 'Cancel'), ('copy', 'Duplicate')]},
        },
        'copy': {
            'actions': [],
            'result': {'type': 'action', 'action':_copy_prp, 'state':'end'}
        }
    }
wizard_prop_copy("wizard_prop_copy")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: