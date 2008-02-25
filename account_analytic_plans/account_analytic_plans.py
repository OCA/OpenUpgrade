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
from osv import fields, osv,orm
import ir

class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        print "one2many_mod2:context:::",context
        print "object::::",dir(obj)
        print "ids::::",ids
        print "name::::",name
        print "values:::",values
        if not values:
            values = {}
        res = {}
        for id in ids:
            res[id] = []
        ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids)], limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            res[r[self._fields_id]].append( r['id'] )
        return res

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
          'name':fields.char('Plan Name',size=64),
          'account_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account Id'),
          'account1_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account1 Id'),
          'account2_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account2 Id'),
          'account3_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account3 Id'),
          'account4_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account4 Id'),
          'account5_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account5 Id'),
          'account6_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account6 Id'),
          'model':fields.boolean('Model', readonly=True),
              }
    _defaults = {
            'model': lambda *args: False,
        }
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
        wiz_id = self.pool.get('ir.actions.wizard').search(cr, uid, [("wiz_name","=","create.model")])
        res = super(account_analytic_plan_instance,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
        if (res['type']=='form'):
            if context.get('journal_id',False):
                rec = self.pool.get('account.journal').browse(cr, uid, [int(context['journal_id'])], context)[0]
                i=1
                res['arch'] = """<form string="%s">/n<field name="name"/>/n<field name="model"/>/n"""%rec.plan_id.name

                for line in rec.plan_id.plan_ids:
                    res['arch']+="""
                    <field name="account%d_ids" string="%s" colspan="4">
                    <tree string="%s" editable="bottom">
                        <field name="analytic_account_id" domain="[('parent_id','child_of','%d')]"/>
                        <field name="rate"/>
                    </tree>
                </field>
                <newline/>
                """%(i,line.name,line.name,line.root_analytic_id)
                    i+=1
                res['arch']+="""<button name="%d" string="Create a Model" type="action" colspan="4"/>/n
                </form>"""%(wiz_id[0])
            else:

                res['arch'] = """<form string="Analytic Entries">
                    <field name="name"/>
                    <field name="model"/>
                    <field name="account_ids" string="Projects" colspan="4">
                        <tree string="Projects" editable="bottom">
                            <field name="analytic_account_id"/>
                            <field name="rate"/>
                        </tree>
                    </field>
                    <newline/>

                    <button name="%d" string="Create a Model" type="action" colspan="4"/>
                </form>"""%(wiz_id[0])

            doc = dom.minidom.parseString(res['arch'])
            xarch, xfields = self._orm__view_look_dom_arch(cr, uid, doc, context=context)
            res['arch'] = xarch
            res['fields'] = xfields
            return res
        else:
            return res
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        new_copy=self.copy(cr, uid, ids[0], context=context)
        vals['model']=False
        result = super(account_analytic_plan_instance, self).write(cr, uid, ids, vals, context)
        return result
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

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        print "in account move line write:ids::::",ids
        result = super(account_move_line, self).write(cr, uid, ids, vals, context)
        return result

    def create(self, cr, uid, vals, context=None, check=True):
        print "in account move line create:vals::::",vals
        result = super(account_move_line, self).create(cr, uid, vals, context)
        return result
account_move_line()

