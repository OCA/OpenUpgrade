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
import tools
from tools.config import config
from tools.translate import _
import netsvc
import time

class project_project(osv.osv):
    _inherit = "project.project"
    _columns = {
                "section_bug_id": fields.many2one('crm.case.section','Bug Section'),
                "section_feature_id": fields.many2one('crm.case.section','Feature Section'),
                "section_support_id": fields.many2one('crm.case.section','Support Section'),                
                
    }   
project_project()

class crm_case(osv.osv):
    _inherit = 'crm.case'
    _columns = {
                'project_id' : fields.many2one('project.project', 'Project', size=64),
    }   
    
    def create(self, cr, uid, values, *args, **kwargs):
        case_id = super(crm_case, self).create(cr, uid, values, *args, **kwargs)
        cr.commit()
        case = self.browse(cr, uid, case_id)
        if case.project_id:         
            self.pool.get('project.project')._log_event(cr, uid, case.project_id.id, {
                                'res_id' : case.id,
                                'name' : case.name, 
                                'description' : case.description, 
                                'user_id': uid, 
                                'action' : 'create',
                                'type'   : 'case'})
        return case_id
    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(crm_case, self).write(cr, uid, ids, vals, context={})
        cr.commit()
        case = self.browse(cr, uid, res)
        if case.project_id:         
            self.pool.get('project.project')._log_event(cr, uid, case.project_id.id, {
                                'res_id' : case.id,
                                'name' : case.name, 
                                'description' : case.description, 
                                'user_id': uid, 
                                'action' : 'write',
                                'type' : 'case'})
        return res
crm_case()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
