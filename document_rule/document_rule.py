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

from tools.misc import currency
MAX_LEVEL = 15
import pooler
import re

class document_rule(osv.osv):
    _name = "document.rule"
    _description = "Document Rule"
    _columns = {
                'name': fields.char('Rule Name', size=64, required=True),
                'date':fields.datetime('Date Creation', readonly=1),
                'author':fields.many2one('res.users','Author'),
                'partner_id':fields.many2one('res.partner', 'Partner', select=1),
                'directory_id': fields.many2one('document.directory', 'Directory'),
                'server_act':fields.many2one('ir.actions.server', 'Action'),
                'active': fields.boolean('Active'),
                'sequence': fields.integer('Sequence'),
                'act_copy_directory_id':fields.many2one('document.directory', 'Copy to'),
                'act_move_directory_id':fields.many2one('document.directory', 'Move to'),
                'act_assign_user_id': fields.many2one('res.users', 'Assign to User'),
                'act_assign_partner_id': fields.many2one('res.partner', 'Assign to Partner'),
                'regex_title' : fields.char('Regular Expression on Title', size=128),
                'regex_filename' : fields.char('Regular Expression on filename', size=128),
                'resource_object':fields.char('Resource Model',size=64),
                'ressource_id': fields.integer('Resource ID'),
                'trg_date_range': fields.integer('Delay after  date'),
                'trg_date_type':  fields.selection([
                                                    ('none','None'),
                                                    ('create','Creation Date'),
                                                    ('action_last','Last Action Date'),
                                                    ], 'Trigger Date', size=16),
                'trg_date_range_type': fields.selection([('minutes', 'Minutes'),('hour','Hours'),('day','Days'),('month','Months')], 'Delay type'),
                'flag':fields.boolean('Flag'),
                }


    _defaults = {
        'active': lambda *a: 1,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'trg_date_range_type': lambda *a: 'day',
        'trg_date_type': lambda *a: 'None',
        'flag': lambda *a: 1,
        }
    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to document rule

        '''
        cr.execute('select * from ir_attachment   where \
                 date_action_next<=%s or date_action_next is null',
                (time.strftime("%Y-%m-%d %H:%M:%S"),))

        ids2 = map(lambda x: x[0], cr.fetchall() or [])
        rule_obj = self.pool.get('ir.attachment')
        attach = rule_obj.browse(cr, uid, ids2, context)
        return rule_obj._action(cr, uid, attach, context=context)

document_rule()


class document_file_rule(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
                    'date_action_next': fields.datetime('Next Action', readonly=1),
                    'act':fields.boolean('Action'),
        }
    _defaults = {
                    'act': lambda *a: 0,
        }
    def _action(self, cr, uid, attach,  context={}):
        action_ids = self.pool.get('document.rule').search(cr, uid, [])
        level = MAX_LEVEL

        while len(action_ids) and level:
            newactions = []
            actions = self.pool.get('document.rule').browse(cr, uid, action_ids, context)
            for attch in attach:
                if not attch.act:
                    for action in actions:
                        ok = True
                        if action.ressource_id:
                            ok = ok and action.ressource_id.id==attch.res_id.id
                        if action.resource_object:
                          ok = ok and action.resource_object.id==attch.res_model.id
                        if action.directory_id:
                            ok = ok and  action.directory_id.id==attch.parent_id.id
                        if action.partner_id.id:
                            ok = ok and action.partner_id.id==attch.partner_id.id
                        if action.author:
                            ok = ok and action.author.id==attch.user_id.id
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
                            patten=re.compile(".*\.([a-zA-Z0-9]|[a-zA-Z0-9])", re.IGNORECASE)
                            if patten.match(regex_filename):
                                 _result =True
                            if not _result:
                                result_filename = False
                        regex_h = not regex_filename or result_filename
                        ok = ok and regex_h
                        if not ok:
                            continue

                        write = {}
                        if ok :
                            if action.server_act:
                                context.update({'active_id':case.id,'active_ids':[attch.id]})
                                self.pool.get('ir.actions.server').run(cr, uid, [action.server_action_id.id], context)
                            write = {}
                            copy={}
                            if action.act_copy_directory_id :
                                copy['parent_id'] = action.act_copy_directory_id.id
                                self.copy(cr, uid, attch.id, copy, context=context)
                            if action.act_assign_partner_id:
                                write['partner_id'] = action.act_assign_partner_id.id
                            if action.act_assign_user_id:
                                write['user_id'] = action.act_assign_user_id.id
                            if action.act_move_directory_id:
                                write['parent_id'] = action.act_move_directory_id.id
                            write['act']= True
                            self.write(cr, uid, [attch.id], write, context)
                            break

            action_ids = newactions
            level -= 1

        return True

document_file_rule()
