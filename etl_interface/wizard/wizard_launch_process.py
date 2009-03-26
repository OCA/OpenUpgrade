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
import netsvc
import pooler


def _open_process(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    obj_process=pool.get('etl.job.process')
    obj_job=pool.get('etl.job')
    process_ids = []
    for id in data['ids']:
        job = obj_job.browse(cr, uid, id)
        if job.state == 'open':
            name = pool.get('ir.sequence').get(cr, uid, 'etl.job.process')
            process_id=obj_process.create(cr, uid, {'name': name, 'job_id': id})
            process_ids.append(process_id)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'etl.job.process', process_id, 'action_open', cr)
    cr.execute('select id,name from ir_ui_view where model=%s and type=%s', ('etl.job.process', 'tree'))
    view_res = cr.fetchone()
    return {
    'name': 'Job Process', 
    'view_type': 'form', 
    'view_mode': 'tree,form', 
    'res_model': 'etl.job.process', 
    'view_id': view_res, 
    'type': 'ir.actions.act_window', 
    'domain' : "[('id','in',%s)]" % process_ids
    }

class open_process(wizard.interface):
    states = {
        'init' : {
            'actions' : [], 
            'result' : {'type' : 'action', 
                    'action' : _open_process, 
                    'state' : 'end'}
        }, 
    }
open_process("etl.launch.job.process")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

