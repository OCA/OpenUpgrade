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

from osv import fields, osv
import pooler

class project_task(osv.osv):
    _inherit = "project.task"
    _columns = {
                'case_id': fields.many2one('crm.case','CRM Case'),
    }
    
    def synch(self, cr, uid, ids, *args):
        crm_case_obj = self.pool.get('crm.case')
        crm_case_section_obj = self.pool.get('crm.case.section')
        section_ids = crm_case_section_obj.search(cr, uid, [('code','=','Mtngs')])
        if not len(section_ids):
            raise osv.except_osv(_('Error !'), _('No Meeting section exits.'))
        for task in self.browse(cr,uid,ids):        
            vals = {'date':task.date_deadline,'user_id':task.user_id.id,'name':task.name,'section_id':section_ids[0]}
            case_id = crm_case_obj.create(cr,uid,vals)
            self.write(cr, uid, task.id, {'case_id':case_id})
        return True
    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(project_task,self).write(cr, uid, ids, vals, context)
        date_deadline = vals.get('date_deadline', False)
        if date_deadline:
            for task in self.browse(cr, uid, ids, context):
                if task.case_id:         
                    cr.execute("update crm_case set date = '%s' where id = %d " %(date_deadline, task.case_id.id))                                  
        return res
       
    

        
project_task()

class crm_case(osv.osv):
    _inherit = "crm.case"
   
    def write(self, cr, uid, ids,vals,context={}):
        res = super(crm_case,self).write(cr, uid, ids, vals, context)
        date = vals.get('date',False)
        if date:
            for case in self.browse(cr, uid, ids, context):
                prj_ids = self.pool.get('project.task').search(cr, uid, [('case_id', '=', case.id)])
                for project_id in prj_ids:
                    cr.execute("update project_task set date_deadline = '%s' where id = %d " %(date,project_id))
        return res 

crm_case()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
