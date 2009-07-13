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
import threading
import pooler

parameter_form = '''<?xml version="1.0"?>
<form string="Scheduler Parameters" colspan="4">
    <label string="This will run all scheduled process which are in Open State" />
</form>'''

parameter_fields = {
}

def _run_process(self, db_name, uid, data, context):
    db, pool = pooler.get_db_and_pool(db_name)
    cr = db.cursor()
    process_obj = pool.get('etl.job.process')
    process_obj.run_scheduler(cr, uid, False, use_new_cursor=cr.dbname,\
            context=context)
    cr.close()
    return {}

def _run_scheduled_processes(self, cr, uid, data, context):
    threaded_calculation = threading.Thread(target=_run_process, args=(self, cr.dbname, uid, data, context))
    threaded_calculation.start()
    return {}

class run_scheduled_job_processes(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':parameter_form, 'fields': parameter_fields, 'state':[('end','Cancel'),('run','Run') ]}
        },
        'run': {
            'actions': [_run_scheduled_processes],
            'result': {'type': 'state', 'state':'end'}
        },
    }
run_scheduled_job_processes('etl.run.scheduled.job.processes')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

