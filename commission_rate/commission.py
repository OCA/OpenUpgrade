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

class report_commission_month(osv.osv):
    _name = "report.commission.month"
    _description = "Commission of month"
    _auto = False
    _columns = {
        'name': fields.char('Sales Agent Name',size=64, readonly=True, select=True),
        'sono':fields.char('Sales Order No',size=64, readonly=True, select=True),
        'invno':fields.char('Invoice Number',size=64, readonly=True, select=True),
        'product_quantity':fields.integer('Product Quantity', readonly=True, select=True),
        'productname':fields.char('Product Name',size=256, readonly=True, select=True),
        'inv_total':fields.float('Invoice Amount', readonly=True, select=True),
        'in_date': fields.date('Invoice Date', readonly=True, select=True),
        'comrate': fields.float('Commission Rate (%)', readonly=True, select=True),
        'commission': fields.float('Commissions Amount', readonly=True, select=True),
#        'state': fields.char('Invoice State', size=64,readonly=True, select=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Canceled')
        ],'Invoice State', select=True),
        'pdate': fields.date('Invoice Paid Date', readonly=True, select=True),

    }
    order = 'name,sono,state,productname'


    def init(self, cr):
        print "In init of commision month ..";
        cr.execute("""
CREATE OR REPLACE VIEW report_commission_month AS( select * from (select al.id AS id,
sg.name as name,
so.name as sono,
ai.number as invno,
al.quantity as product_quantity,
al.name as productname,
(al.quantity * al.price_unit) as inv_total,
ai.date_invoice as in_date,
sg.commission_rate as comrate,
(al.quantity *al.price_unit * sg.commission_rate / 100) as commission,
ai.state,
'' as pdate
from
account_invoice ai,
sale_order so,
account_invoice_line al,
res_partner p,
sale_agent sg

where ai.origin=so.name
and ai.state in ('draft','open','proforma','cancel')
and al.invoice_id=ai.id and p.id=ai.partner_id
and sg.id=p.agent_id


)
 as a

UNION

(

select al.id  AS id,
sg.name as name,
so.name as sono,
ai.number as invno,
al.quantity as product_quantity,
al.name as productname,
(al.quantity * al.price_unit) as inv_total,
ai.date_invoice as in_date,
sg.commission_rate as comrate,
(al.quantity *al.price_unit * sg.commission_rate / 100) as commission,
ai.state,
ar.name as pdate
from
account_invoice ai,
account_move am,
account_move_line aml,

account_move_reconcile ar,
sale_order so,
account_invoice_line al,
res_partner p,
sale_agent sg

where ai.origin=so.name
and ai.state in ('paid')
and al.invoice_id=ai.id and p.id=ai.partner_id
and sg.id=p.agent_id and ai.move_id=am.id
and aml.move_id=am.id
and ar.id = aml.reconcile_id

))""")
report_commission_month()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

