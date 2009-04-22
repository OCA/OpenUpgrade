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

from mx.DateTime import now

import wizard
import netsvc
import ir
import pooler
import tools
from tools.translate import _
from osv import osv

def _select_report(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    obj = pool.get('maintenance.maintenance').browse(cr, uid, data['ids'])[0]
    if obj.type_id.name=='Basic':
        return 'basic'    
    elif obj.type_id.name=='Corporate':
        return 'corporate'
    elif obj.type_id.name=='SMB':
        return 'smb'
    else:
        return 'basic'
class wizard_print_contract(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'choice', 'next_state':_select_report}
        },
        'basic': {
            'actions': [],
            'result': {'type': 'print', 'report':'maintenance.basic.contract', 'state':'end'}
        },
        'corporate': {
            'actions': [],
            'result': {'type': 'print', 'report':'maintenance.corporate.contract', 'state':'end'}
        },
        'smb': {
            'actions': [],
            'result': {'type': 'print', 'report':'maintenance.smb.contract', 'state':'end'},
#        'finish':{
#             'actions': [],
#             'result': {'type': 'state', 'state': 'end'}
#               }
        },
    }
wizard_print_contract('wizard.print.maintenance.contract')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

