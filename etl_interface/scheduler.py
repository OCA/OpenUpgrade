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

from osv import osv
import netsvc
import pooler
from mx import DateTime
import time

class etl_job_process(osv.osv):
    _inherit = 'etl.job.process'
    
    def _start_job_process(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        if not context:
            context={}
        maxdate = DateTime.now() 

        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        wf_service = netsvc.LocalService("workflow")
        
        process_obj = self.pool.get('etl.job.process')
        if not ids:
            ids=process_obj.search(cr, uid,[('state','=','open')])
        for process in process_obj.browse(cr, uid,ids):
            if process.schedule_date:
                if maxdate.strftime('%Y-%m-%d %H:%M:%S')>=process.schedule_date:
                    wf_service.trg_validate(uid, 'etl.job.process', process.id, 'start_process', cr)
        if use_new_cursor:
            cr.commit()


etl_job_process()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
