 #-*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import time
import netsvc
from osv import fields, osv
MAX_LEVEL = 15
from tools.misc import currency

import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime


class document_rule(osv.osv):
    _name = "document.rule"
    _description = "Document Rule"
    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'author':fields.many2one('res.users','Author'),
                'partner_id':fields.many2one('res.partner', 'Partner', select=1),
                'directory_id': fields.many2one('document.directory', 'Directory'),
                'date_type':  fields.selection([('none','None'),
                                                    ('create','Creation Date'),], 'Trigger Date', size=16),
                'server_act':fields.many2one('ir.actions.server', 'Action'),
                'filename':fields.many2one('ir.attachment','File'),
                'resource_object':fields.char('Resource Name',size=64),
                'active': fields.boolean('Active'),
                'sequence': fields.integer('Sequence'),
                'regex_title' : fields.char('Regular Expression on Title', size=128),
                'regex_filename' : fields.char('Regular Expression on filename', size=128),
                'resource_object':fields.char('Resource Model',size=64),
                'ressource_id': fields.integer('Resource ID'),
                'act_copy_directory_id':fields.many2one('document.directory', 'Copy to'),
                'act_move_directory_id':fields.many2one('document.directory', 'Move to'),
                'act_assign_user_id': fields.many2one('res.users', 'Assign to User'),
                'act_assign_partner_id': fields.many2one('res.partner', 'Assign to Partner'),

                }
    _defaults = {
        'active': lambda *a: 1,
        }
    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to document rule

        '''
        cr.execute('select attach.id, attach.datas_fname from ir_attachment attach, document_rule rule \
                    where attach.partner_id = rule.partner_id \
                    or rule.directory_id = attach.parent_id \
                    or attach.user_id=rule.author\
                    or attach.res_id=rule.ressource_id \
                    or attach.res_model=rule.resource_object'
                    )
        ids2 = map(lambda x: x[0], cr.fetchall() or [])
        rule_obj = self.pool.get('ir.attachment')
        attach = rule_obj.browse(cr, uid, ids2, context)
        return rule_obj._action(cr, uid, attach, context=context)

document_rule()


class document_file(osv.osv):
    _inherit = 'ir.attachment'
    def _action(self, cr, uid, attach,  context={}):
        action_ids = self.pool.get('document.rule').search(cr, uid, [])
        level = MAX_LEVEL
        while len(action_ids) and level:
            newactions = []
            actions = self.pool.get('document.rule').browse(cr, uid, action_ids, context)
            for attch in attach:
                for action in actions:
                    ok = True
                    reg_name = action.regex_title
                    result_name = True
                    if reg_name:
                        ptrn = re.compile(str(reg_name))
                        _result = ptrn.search(str(attch.title))
                        if not _result:
                            result_name = False
                    regex_n = not reg_name or result_name
                    ok = ok and regex_n
                    regex_filename = action.regex_filename
                    result_filename = True
                    if regex_filename:
                        ptrn = re.compile(str(regex_filename))
                        _result = ptrn.search(str(attch.datas_fname))
                        if not _result:
                            result_filename = False
                    regex_h = not regex_filename or result_filename
                    ok = ok and regex_h
                    if not ok:
                        continue
                    if ok:
                        if action.server_act:
                            context.update({'active_id':case.id,'active_ids':[attch.id]})
                            self.pool.get('ir.actions.server').run(cr, uid, [action.server_action_id.id], context)
                        write = {}
                        if action.act_copy_directory_id:
                            write['partner_id'] = action.act_assign_partner_id.id
                            self.copy(cr, uid, attch.id, write, context=context)
                        if action.act_assign_partner_id:
                            attch.partner_id = action.act_assign_partner_id
                            write['partner_id'] = action.act_assign_partner_id.id
                        if action.act_assign_user_id:
                            write['user_id'] = action.act_assign_user_id.id
                        if action.act_move_directory_id:
                            write['parent_id'] = action.act_move_directory_id.id
                        self.write(cr, uid, [attch.id], write, context)

            action_ids = newactions
            level -= 1
        return True

document_file()



