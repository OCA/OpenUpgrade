#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
from osv import osv
from osv import fields

class account_loan_proof_type(osv.osv):
    _name="account.loan.proof.type"
    _columns={
        'name':fields.char('Proof Type Name',size=64,required=True),
        'shortcut':fields.char("Shortcut",size=32,required=True),
    }
account_loan_proof_type()

def _account_loan_proof_type_get(self,cr,uid,context={}):
    obj = self.pool.get('account.loan.proof.type')
    ids = obj.search(cr, uid,[('name','ilike','')])
    res = obj.read(cr, uid, ids, ['shortcut','name'], context)
    return [(r['name'], r['name']) for r in res]

class account_loan_proof(osv.osv):
    _name='account.loan.proof'
    _columns = {
        'name': fields.char('Proof name',size=256,required=True),
        'loan_id': fields.many2one('account.loan', 'Loan'),
        'note':fields.text('Proof Note'),
        'document':fields.binary('Proof Document'),
        'type': fields.selection(_account_loan_proof_type_get,'Type',select=True),
        'state': fields.selection(
            [
                ('draft','Draft'),
                ('apply','Under Varification'),
                ('done','Varified'),
                ('cancel','Cancel')
            ],'State', readonly=True, select=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    def default_get(self, cr, uid, fields, context={}):
        data = self._default_get(cr, uid, fields, context)
        for f in data.keys():
            if f not in fields:
                del data[f]
        return data
    
    def _default_get(self, cr, uid, fields, context={}):
        data = super(account_loan_proof, self).default_get(cr, uid, fields, context)
        if context and context.has_key('loan_id'):
            if not context['loan_id']:
                raise osv.except_osv(_('Error !'), _('Please Save Record First'))
            data['loan_id']=context['loan_id']
        return data

    def apply_varification(self, cr, uid, ids,context = {}):
        self.pool.get('account.loan.proof').write(cr,uid,ids,{'state':'apply'})
        return True

    def proof_varified(self,cr,uid,ids,context = {}):
        self.pool.get('account.loan.proof').write(cr,uid,ids,{'state':'done'})
        return True
    
    def proof_canceled(self,cr,uid,ids,context = {}):
        self.pool.get('account.loan.proof').write(cr,uid,ids,{'state':'cancel'})
        return True

account_loan_proof()
