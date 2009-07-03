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

class invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_next_followup(self, cr, uid, ids, field_names, args, context=None):
        result = {}
        for i in ids:
            result[i] = dict.fromkeys(field_names, False)
        
        for i in range(0, len(ids), cr.IN_MAX):
            sub_ids = ids[i:i+cr.IN_MAX]

            cr.execute('''SELECT invoice_id,
                                 to_char("date", 'YYYY-MM-DD HH24:MI:SS') AS proforma_next_followup_scheduled_at,
                                 followup_action_id AS proforma_next_followup_action_id
                            FROM proforma_followup_scheduler
                           WHERE invoice_id IN (%s)''' % ','.join(['%s']*len(sub_ids)), sub_ids)
            for qr in cr.dictfetchall():
                iid = qr.pop('invoice_id')
                for fn in field_names:
                    if fn in qr:
                        result[iid][fn] = qr[fn]

        return result

            
    _columns = {
        'proforma_followup_history_ids': fields.one2many('proforma.followup.history', 'invoice_id', string='Executed Followups', readonly=True),
        'proforma_next_followup_scheduled_at': fields.function(_get_next_followup, method=True, multi='followup', type='datetime', string='Scheduled at'),
        'proforma_next_followup_action_id': fields.function(_get_next_followup, method=True, multi='followup', type='many2one', relation='proforma.followup.action', string='Next Action'),
    }

invoice()

