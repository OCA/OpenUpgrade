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

class account_loan_loantype(osv.osv):
    _name = "account.loan.loantype"
    _description = "account loan type "
    _columns = {
        'name' : fields.char('Type Name', size=32,required=True),
        'prooftypes' : fields.many2many('account.loan.proof.type', 'loantype_prooftype_rel', 'order_line_id', 'tax_id', 'Taxes'),
        'calculation':fields.selection(
            [
                ('flat','Flat'),
                ('reducing','Reducing')
            ],'Calculation Method'),
        'interestversion_ids' : fields.one2many('account.loan.loantype.interestversion','loantype_id','Interest Versions'),
    }
account_loan_loantype()

class account_loan_loantype_interestversion(osv.osv):
    _name='account.loan.loantype.interestversion'
    _columns={
        'name':fields.char('Name',size=32,required=True),
        'loantype_id':fields.many2one('account.loan.loantype','Loan Type'),
        'start_date':fields.date('Start Date'),
        'end_date':fields.date('End Date'),
        'active':fields.boolean('Active'),
        'interestversionline_ids':fields.one2many('account.loan.loantype.interestversionline','interestversion_id','Current Interest Version'),
        'sequence':fields.integer('Sequence',size=32),
    }
    _order = 'sequence'
    _defaults = {
        'active': lambda *a: True,
    }
account_loan_loantype_interestversion()

class account_loan_loantype_interestversionline(osv.osv):
    _name='account.loan.loantype.interestversionline'
    _columns={
        'name':fields.char('Interest ID',size=32,required=True),
        'interestversion_id':fields.many2one('account.loan.loantype.interestversion','Loan Interest Id'),
        'min_month' : fields.integer('Minimum Month',size=32),
        'max_month' : fields.integer('Maximum Month',size=32),
        'min_amount': fields.float('Minimum Amount', digits=(10,2)),
        'max_amount': fields.float('Maximum Amount', digits=(10,2)),
        'rate':fields.float('Rate',digits=(10,2)),
        'sequence':fields.integer('Sequence',size=32),
    }
    _order = 'sequence'
account_loan_loantype_interestversionline()

