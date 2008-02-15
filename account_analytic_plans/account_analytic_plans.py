# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from xml import dom

from mx import DateTime
from mx.DateTime import now
import time

import netsvc
from osv import fields, osv
import ir

class account_analytic_plan(osv.osv):
    _name = "account.analytic.plan"
    _description = "Analytic Plans"
    _columns = {
        'name': fields.char('Plan Name', size=64, required=True, select=True,),
        'plan_ids': fields.one2many('account.analytic.plan.line','plan_id','Analytic Plans'),
    }

account_analytic_plan()

class account_analytic_plan_line(osv.osv):
    _name = "account.analytic.plan.line"
    _description = "Analytic Plan Lines"
    _columns = {
        'plan_id':fields.many2one('account.analytic.plan','Plan Name'),
        'name': fields.char('Plan Name', size=64, required=True, select=True),
        'sequence':fields.integer('Sequence'),
        'root_analytic_id': fields.many2one('account.analytic.account','Root Account',help="Root account of this plan."),
        'default_analytic_id':fields.many2one('account.analytic.account','Default Account',help="Default account of this plan."),
    }
    _order = "sequence,id"

account_analytic_plan_line()

class account_analytic_plan_instance(osv.osv):
    _name='account.analytic.plan.instance'
    _description = 'Object for create analytic entries from invoice lines'
    _columns={
          'account_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account Id'),
          'account1_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account1 Id'),
          'account2_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account2 Id'),
          'account3_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account3 Id'),
          'account4_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account4 Id'),
          'account5_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account5 Id'),
          'account6_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account6 Id'),
              }

account_analytic_plan_instance()

class account_analytic_plan_instance_line(osv.osv):
    _name='account.analytic.plan.instance.line'
    _description = 'Object for create analytic entries from invoice lines'
    _columns={
          'plan_id':fields.many2one('account.analytic.plan.instance','Plan Id'),
          'analytic_account_id':fields.many2one('account.analytic.account','Analytic Account'),
          'rate':fields.float('Rate (%)'),
          'generated_line_id':fields.many2one('account.analytic.line','Generated Line Id'),
              }
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['analytic_account_id'], context)
        res = []
        for record in reads:
            res.append((record['id'], record['analytic_account_id']))
        return res

account_analytic_plan_instance_line()

class account_journal(osv.osv):
    _inherit='account.journal'
    _name='account.journal'
    _columns = {
            'plan_id':fields.many2one('account.analytic.plan','Plan Name'),
                }
account_journal()

class account_invoice_line(osv.osv):
    _inherit='account.invoice.line'
    _name='account.invoice.line'
    _columns = {
            'analytics_id':fields.many2one('account.analytic.plan.instance','Analytic Account'),
                }
account_invoice_line()

class account_move_line(osv.osv):
    _inherit='account.move.line'
    _name='account.move.line'
    _columns = {
            'analytics_id':fields.many2one('account.analytic.plan.instance','Analytic Account'),
                }
account_move_line()

