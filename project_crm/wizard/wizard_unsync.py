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

import wizard
import pooler

ask_form = """<?xml version="1.0" ?>
<form string="Unsynchronize Event">    
</form>"""

ask_fields = {
    
}

class wizard_unsync(wizard.interface):
    
    def unsync(self,cr,uid,data,context):
        prj_obj=pooler.get_pool(cr.dbname).get('project.task')
        prj_obj.write(cr, uid, data['ids'],{'case_id':False}, context)
        return {}

    def delete(self,cr, uid,data,context):
        for project in pooler.get_pool(cr.dbname).get('project.task').browse(cr, uid, data['ids']):
            if project.case_id:            
                pooler.get_pool(cr.dbname).get('crm.case').unlink(cr, uid, [project.case_id.id], context)
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':ask_form, 'fields':ask_fields, 'state':[
                ('unsync', 'Unsynchronize'),
                ('delete','Delete')
            ]},
        },
        'unsync': {
            'actions': [unsync],
            'result': {'type':'state', 'state':'end'},
                    },
                
        'delete': {
            'actions': [delete],
            'result': {'type':'state', 'state':'end'},
                    },
    }
wizard_unsync('wizard_unsync')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

