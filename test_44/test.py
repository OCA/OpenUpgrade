# -*- encoding: utf-8 -*-
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

from osv import fields,osv

class test_temporal(osv.osv_memory):
    _name = 'test.temporal'
    def _get_partner(self,cr, uid, ctx):
        if 'action_id' in ctx:
            return self.pool.get('res.partner').name_get(cr, uid, [ctx['action_id']])[0]
        return False
    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'line_ids': fields.one2many('test.temporal.line', 'temporal_id', 'Lines', invisible=True, states={'confirm':[('invisible',False)]}),
        'state': fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done')], 'State'),
        'partner_ids': fields.many2many('res.partner', 'res_partner_test_rel', 'partner_id', 'test_id', 'Partners', states={'draft':[('readonly',True), ('invisible',True)]}),
    }
    _defaults = {
        'state': lambda self,cr,uid,ctx: 'draft',
        'partner_id':  _get_partner
    }
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context)
        return self.get_action(cr, uid, ids, context)

    def get_action(self, cr, uid, ids, context=None):
        if 'action_id' not in (context or {}):
            return False
        value = {
            'domain': "[('partner_id','=',%d)]" % (context['action_id'],),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return value
test_temporal()

class test_temporal_line(osv.osv_memory):
    _name = 'test.temporal.line'
    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'length': fields.integer('Size'),
        'temporal_id': fields.many2one('test.temporal', 'Temporal'),
    }
test_temporal_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

