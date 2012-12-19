# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
from openerp import tools

from openerp.tools.translate import _
from openerp.tools import ustr
from openerp.osv import fields
from openerp.osv import osv

import crm

class base_action_rule(osv.osv):
    """ Base Action Rule """
    _inherit = 'base.action.rule'
    _description = 'Action Rules'

    _columns = {
        'trg_section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'trg_max_history': fields.integer('Maximum Communication History'),
        'trg_categ_id':  fields.many2one('crm.case.categ', 'Category'),
        'regex_history' : fields.char('Regular Expression on Case History', size=128),
        'act_section_id': fields.many2one('crm.case.section', 'Set Team to'),
        'act_categ_id': fields.many2one('crm.case.categ', 'Set Category to'),
    }

    def do_check(self, cr, uid, action, obj, context=None):
        ok = super(base_action_rule, self).do_check(cr, uid, action, obj, context=context)

        if hasattr(obj, 'section_id'):
            ok = ok and (not action.trg_section_id or action.trg_section_id.id == obj.section_id.id)
        if hasattr(obj, 'categ_ids'):
            ok = ok and (not action.trg_categ_id or action.trg_categ_id.id in [x.id for x in obj.categ_ids])

        #Cheking for history
        regex = action.regex_history
        if regex:
            res = False
            ptrn = re.compile(ustr(regex))
            for history in obj.message_ids:
                _result = ptrn.search(ustr(history.subject))
                if _result:
                    res = True
                    break
            ok = ok and res

        if action.trg_max_history:
            res_count = False
            history_ids = filter(lambda x: x.email_from, obj.message_ids)
            if len(history_ids) <= action.trg_max_history:
                res_count = True
            ok = ok and res_count
        return ok

    def do_action(self, cr, uid, action, obj, context=None):
        res = super(base_action_rule, self).do_action(cr, uid, action, obj, context=context)
        model_obj = self.pool.get(action.model_id.model)
        write = {}
        if hasattr(action, 'act_section_id') and action.act_section_id:
            write['section_id'] = action.act_section_id.id

        if hasattr(action, 'act_categ_id') and action.act_categ_id:
            write['categ_ids'] = [(4, action.act_categ_id.id)]

        model_obj.write(cr, uid, [obj.id], write, context)
        return res

    def state_get(self, cr, uid, context=None):
        """Gets available states for crm"""
        res = super(base_action_rule, self).state_get(cr, uid, context=context)
        return res + crm.AVAILABLE_STATES

    def priority_get(self, cr, uid, context=None):
        res = super(base_action_rule, self).priority_get(cr, uid, context=context)
        return res + crm.AVAILABLE_PRIORITIES

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
