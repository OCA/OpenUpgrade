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

def _check_sections(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    data_obj = pool.get('ir.model.data')
    sec_obj = pool.get('crm.case.section')
    bug_id = sec_obj.search(cr, uid, [('code','=','BugSup')])
    if not bug_id:
        raise wizard.except_wizard(_('Error !'),
            _('You did not installed the Bug Tracking when you configured the crm_configuration module.' \
              '\nyou must create a section with the code \'BugSup\'.'
              ))
    else:
        id1 = data_obj._get_id(cr, uid, 'crm_configuration', 'crm_case_form_view')
        if id1:
            id1 = data_obj.browse(cr, uid, id1, context=context).res_id
        return {
            'domain':"[('section_id.name','=','Bug Tracking')]",
            'name': _('New Bug'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.case',
            'view_id': False,
            'views': [(id1,'form')],
            'type': 'ir.actions.act_window',
            }
        
class check_section(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action':_check_sections, 'state' : 'end'}
        },
    }
check_section('portal.crm.check.section')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: