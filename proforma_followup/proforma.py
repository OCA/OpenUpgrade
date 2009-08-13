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
import time
import tools.sql

def str2dict(s):
    return eval('dict(%s)' % (s,))


class proforma_followup_action(osv.osv):
    _name = 'proforma.followup.action'
    _description = 'PRO-Forma Followup Action'
    _order = 'sequence'

    _columns = {
        'name': fields.char('Name', size=64, required=True, select=1),
        'sequence': fields.integer('Step',select=1),
        'days': fields.integer('Days', help='delay by previous action or invoice date'),
        'action_id': fields.many2one('ir.actions.server', 'Action Server', required=True, domain=[('model_id.model', '=', 'account.invoice')]),
        'context': fields.char('Context', size=128),
        'active': fields.boolean('Active', select=1),
    }
        
    _defaults = {
        'active': lambda *a: True,
        'context': lambda *a: '{}',
    }
    
    def _check_context(self, cr, uid, ids, context=None):
        for action in self.browse(cr, uid, ids, context):
            if action.context:
                try:
                    str2dict(action.context)
                except:
                    return False
        return True

    _constraints = [
        (_check_context, 'Invalid Context', ['context']),
    ]

    _sql_constraints = [
        ('sequence_uniq', 'unique(sequence)', 'You can not have two actions at the same step'),
    ]

proforma_followup_action()


class proforma_followup_history(osv.osv):
    _name = 'proforma.followup.history'
    _order = 'create_date,step'
    
    _columns = {
        'name': fields.char('Name', size=132, required=True),   
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='cascade'),
        'create_date': fields.datetime('Followup Date'),
        'step': fields.integer('Step'),
    }

    def create(self, cr, uid, values, context=None):
        raise osv.except_osv(_('Error'), _('You can not create this kind of document'))

    def new(self, cr, uid, followup_action_id, invoice_id, context=None):
        followup_action = self.pool.get('proforma.followup.action').browse(cr, uid, followup_action_id, context)

        values = {
            'name': '%s | %s' % (followup_action.name, followup_action.action_id.name),
            'invoice_id': invoice_id,
            'step': followup_action.sequence,
        }

        return super(proforma_followup_history, self).create(cr, uid, values, context=context)

proforma_followup_history()

class proforma_followup_scheduler(osv.osv):
    # TODO filter on customer invoices ?
    _name = 'proforma.followup.scheduler'
    _auto = False
    _rec_name = 'date'

    _columns = {
        'date': fields.datetime('Next action planned at', readonly=True),
        'followup_action_id': fields.many2one('proforma.followup.action', 'Followup Action', readonly=True), 
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE VIEW "%s" AS ( 
             SELECT sq3.invoice_id as id,
                    sq3.last_action_date + pfa.days * interval '1 day' AS date,
                    pfa.id AS followup_action_id,
                    sq3.invoice_id
               FROM
                    ( SELECT sq2.invoice_id,
                             MIN(pfa.sequence) AS nextstep,
                             sq2.last_action_date
                        FROM
                             (SELECT sq1.invoice_id,
                                     COALESCE(h.create_date, i.date_invoice) AS last_action_date,
                                     COALESCE(sq1.maxstep,(SELECT MIN(sequence)-1
                                                             FROM proforma_followup_action
                                                            WHERE active = 't')
                                     ) AS last_action_step
                                FROM
                                     ( SELECT MAX(h.step) AS maxstep,
                                              i.id AS invoice_id
                                         FROM account_invoice i
                                         LEFT OUTER JOIN proforma_followup_history h ON h.invoice_id = i.id
                                        WHERE i.state = 'proforma2'
                                     GROUP BY i.id
                                     ) sq1
                             LEFT OUTER JOIN proforma_followup_history h ON (h.step = sq1.maxstep AND h.invoice_id = sq1.invoice_id)
                                   LEFT JOIN account_invoice i ON sq1.invoice_id = i.id
                             ) sq2,
                             proforma_followup_action pfa
                       WHERE pfa.active = 't'
                             AND pfa.sequence > sq2.last_action_step
                    GROUP BY sq2.invoice_id,
                             sq2.last_action_date
                    ) sq3,
                    proforma_followup_action pfa
              WHERE pfa.sequence = sq3.nextstep

            )""" % (self._table,)
        )

    def execute(self, cr, uid, context=None):
        if context is None:
            context = {}

        history = self.pool.get('proforma.followup.history')
        now = time.strftime('%Y-%m-%d')
        ids = self.search(cr, uid, [('date', '>=', now)], context=context) 
        for this in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()

            if this.followup_action_id.context:
                factx = str2dict(this.followup_action_id.context)
                ctx.update(factx)

            ctx['active_id'] = this.invoice_id.id
            this.followup_action_id.action_id.run(context=ctx)
            history.new(cr, uid, this.followup_action_id.id, this.invoice_id.id, context=context)
        return True

proforma_followup_scheduler()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
