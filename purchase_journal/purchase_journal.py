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

from osv import osv, fields
import netsvc
import time

class purchase_journal(osv.osv):
    _name = 'purchase_journal.purchase.journal'
    _description = 'purchase Journal'
    _columns = {
        'name': fields.char('Journal', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'user_id': fields.many2one('res.users', 'Responsible', required=True),
        'date': fields.date('Journal date', required=True),
        'date_created': fields.date('Creation date', readonly=True, required=True),
        'date_validation': fields.date('Validation date', readonly=True),
        'purchase_stats_ids': fields.one2many("purchase_journal.purchase.stats", "journal_id", 'purchase Stats', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('open','Open'),
            ('done','Done'),
        ], 'Creation date', required=True),
        'note': fields.text('Note'),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'date_created': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,context: uid,
        'state': lambda self,cr,uid,context: 'draft',
    }
    def button_purchase_cancel(self, cr, uid, ids, context={}):
        for id in ids:
            purchase_ids = self.pool.get('purchase.order').search(cr, uid, [('journal_id','=',id),('state','=','draft')])
            for purchaseid in purchase_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'purchase.order', purchaseid, 'cancel', cr)
        return True
    def button_purchase_confirm(self, cr, uid, ids, context={}):
        for id in ids:
            purchase_ids = self.pool.get('purchase.order').search(cr, uid, [('journal_id','=',id),('state','=','draft')])
            for purchaseid in purchase_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'purchase.order', purchaseid, 'order_confirm', cr)
        return True

    def button_open(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'open'})
        return True
    def button_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    def button_close(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'done', 'date_validation':time.strftime('%Y-%m-%d')})
        return True
purchase_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

