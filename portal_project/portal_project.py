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
        res = super(crm_case, self).create(cr, uid, values, *args, **kwargs)
        prj_ids = self.pool.get('project.project').search(cr, uid, ['|','|',('section_bug_id','=',values['section_id']),('section_feature_id','=',values['section_id']),('section_support_id','=',values['section_id'])])
        if prj_ids:
            for j in prj_ids:
                members = self.pool.get('project.project').browse(cr, uid, [j])[0].members
                for i in members:
                    if tools.email_send(config['email_from'], i.address_id.email, values['name'], values['description'], debug=False, subtype='html') == True:
                        logger = netsvc.Logger()
                        logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (i.address_id.email))
                    else:
                        logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (i.address_id.email))
        return res
    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(crm_case, self).write(cr, uid, ids, vals, context={})
        case_obj = self.browse(cr, uid, ids)[0]
        prj_ids = self.pool.get('project.project').search(cr, uid, ['|','|',('section_bug_id','=',case_obj.section_id.id),('section_feature_id','=',case_obj.section_id.id),('section_support_id','=',case_obj.section_id.id)])
        if prj_ids:
            for j in prj_ids:
                members = self.pool.get('project.project').browse(cr, uid, [j])[0].members
                for i in members:
                    if tools.email_send(config['email_from'], i.address_id.email, case_obj.name, case_obj.description, debug=False, subtype='html') == True:
                        logger = netsvc.Logger()
                        logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (i.address_id.email))
                    else:
                        logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (i.address_id.email))
        return res
crm_case()

class task(osv.osv):
    _inherit = 'project.task'
    
    def create(self, cr, uid, values, *args, **kwargs):
        res = super(task, self).create(cr, uid, values, *args, **kwargs)
        prj_ids = self.pool.get('project.project').search(cr, uid, [('id','=',values['project_id'])])
        if prj_ids:
            members = self.pool.get('project.project').browse(cr, uid, prj_ids)[0].members
            for i in members:
                if tools.email_send(config['email_from'], i.address_id.email, values['name'], values['description'], debug=False, subtype='html') == True:
                    logger = netsvc.Logger()
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (i.address_id.email))
                else:
                    logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (i.address_id.email))
        return res
    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(task, self).write(cr, uid, ids, vals, context={})
        project_obj = self.browse(cr, uid, ids)[0]
        prj_ids = self.pool.get('project.project').search(cr, uid, [('id','=',project_obj.project_id.id)])
        if prj_ids:
            members = self.pool.get('project.project').browse(cr, uid, prj_ids)[0].members
            for i in members:
                if tools.email_send(config['email_from'], i.address_id.email, project_obj.name, project_obj.description, debug=False, subtype='html') == True:
                    logger = netsvc.Logger()
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (i.address_id.email))
                else:
                    logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (i.address_id.email))
        return res
task()

class document_file(osv.osv):
    _inherit = 'ir.attachment'
    
    def create(self, cr, uid, values, *args, **kwargs):
        res = super(document_file, self).create(cr, uid, values, *args, **kwargs)
        if args[0]['default_res_id'] and args[0]['default_res_model'] == 'project.project':
            members = self.pool.get(args[0]['default_res_model']).browse(cr, uid, [args[0]['default_res_id']])[0].members
            for i in members:
                if tools.email_send(config['email_from'], i.address_id.email, values['name'], values['description'], debug=False, subtype='html') == True:
                    logger = netsvc.Logger()
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (i.address_id.email))
                else:
                    logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (i.address_id.email))
        return res
    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(document_file, self).write(cr, uid, ids, vals, context={})
        att_obj = self.browse(cr, uid, ids)[0]
        if att_obj.res_id and att_obj.res_model == 'project.project':
            members = self.pool.get('project.project').browse(cr, uid, [att_obj.res_id])[0].members
            for i in members:
                if tools.email_send(config['email_from'], i.address_id.email, att_obj.name, att_obj.description, debug=False, subtype='html') == True:
                    logger = netsvc.Logger()
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (i.address_id.email))
                else:
                    logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (i.address_id.email))
        return res
document_file()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: