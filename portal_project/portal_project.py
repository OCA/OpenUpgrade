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
         'server_act_id' : fields.many2one('ir.actions.server', 'Action'),        
        }
#    _defaults = {
#           'server_act_id' : lambda self, cr, uid, context=None: \
#                    self.pool.get('ir.actions.server').search(cr, uid, [('name', '=', 'Send email')])[0],      
#            }
    
    def write(self, cr, uid, ids, vals, context={}):
        id = self.pool.get('ir.actions.server').search(cr, uid, [('model_id', '=', 'Case'),('name','=','Send email')])
        if id:
            obj = pooler.get_pool(cr.dbname).get('ir.actions.server')
            return obj.run(cr, uid, id, context=context)
        return False
crm_case()

class task(osv.osv):
    _inherit = 'project.task'
    _columns = {
         'server_act_id' : fields.many2one('ir.actions.server', 'Action'),        
        }
#    _defaults = {
#           'server_act_id' : lambda self, cr, uid, context=None: \
#                    self.pool.get('ir.actions.server').search(cr, uid, [('name', '=', 'Send email')])[0],      
#            }
    
    def write(self, cr, uid, ids, vals, context={}):
        user_id = self.browse(cr, uid, ids)[0].user_id.id
        prj_ids = self.pool.get('project.project').search(cr, uid, [])
        mem = self.pool.get('project.project').browse(cr, uid, prj_ids)[0].members
        for i in mem:
            if user_id in [i.id]:
                id = self.pool.get('ir.actions.server').search(cr, uid, [('model_id', '=', 'Task'),('name','=','Send email')])
                if id:
                    obj = pooler.get_pool(cr.dbname).get('ir.actions.server')
                    return obj.run(cr, uid, id, context=context)
        return False
task()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: