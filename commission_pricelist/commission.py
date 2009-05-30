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
        'name': fields.char('Sales Agent Name',size=64, readonly=True),
        'sono':fields.integer('Sales Order No', readonly=True),
        'invno':fields.integer('Invoice Number', readonly=True),
        'product_quantity':fields.integer('Product Quantity', readonly=True),
        'productname':fields.char('Product Name',size=256, readonly=True),
        'inv_total':fields.float('Invoice Amount', readonly=True),
        'in_date': fields.date('Invoice Date', readonly=True),
        'comrate': fields.float('Commission Rate (%)', readonly=True),
        'commission': fields.float('Commissions Amount', readonly=True),
        'state': fields.char('Invoice State', size=64,readonly=True),
        'pdate': fields.date('Invoice Paid Date', readonly=True),

    }
    _order = 'name,sono,state'

    def init(self, cr):
        cr.execute(""" create or replace view report_commission_month as (select * from (select sg.id as id,sg.name as name,so.name as sono,ai.number as invno,
    al.quantity as product_quantity,al.name as productname,(al.quantity * al.price_unit) as inv_total,to_char(ai.date_invoice, 'YYYY-MM-DD') as in_date,
    ((1-pi.price_discount)*100) as comrate,((al.quantity *al.price_unit)*(1-pi.price_discount))
              as commission,ai.state,'' as pdate
from
account_invoice ai,
sale_order so,
account_invoice_line al,
res_partner p,
sale_agent sg,
product_pricelist_item pi,
product_pricelist_version pv

where ai.origin=so.name
and ai.state in ('draft','open','proforma','cancel')
and al.invoice_id=ai.id and p.id=ai.partner_id
and sg.id=p.agent_id and pi.price_version_id=pv.id

and sg.comprice_id = pv.pricelist_id and pi.price_discount > 0) as a

UNION

(
select min(A.id) as id,A.name as name,S.name as sono,I.number as invno
              ,L.quantity as product_quantity,L.name as productname,(L.quantity * L.price_unit) as inv_total,to_char(I.date_invoice, 'YYYY-MM-DD') as in_date,
              ((1-R.price_discount)*100) as comrate,((L.quantity * L.price_unit)*(1-R.price_discount))
              as commission,I.state,AMR.name as pdate from

sale_agent A,
account_move_reconcile AMR,
res_partner P,
account_invoice I,
product_pricelist_item R,
account_invoice_line L,
sale_order S,
product_pricelist_version PV

 where
I.state='paid' and
R.price_version_id=PV.id AND A.comprice_id = PV.pricelist_id AND I.origin=S.name AND
R.price_discount > 0 AND S.partner_id = P.id AND P.agent_id=A.id AND I.partner_id=P.id AND I.id=L.invoice_id
group by L.quantity, L.price_unit,R.price_discount,I.state,I.id,A.name,P.name,I.state,I.date_invoice,L.name,
S.name,I.number,A.id,AMR.name
)
) """)
report_commission_month()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

