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
import time
from report import report_sxw
import pooler

class total_sold(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(total_sold, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'check_total': self._check_total,
        })
        self.context = context

    def _check_total(self, form, partner):
        pool_obj = pooler.get_pool(self.cr.dbname)
        obj_inv = pool_obj.get('account.invoice')
        obj_lines = pool_obj.get('account.invoice.line')
        inv_ids = obj_inv.search(self.cr, self.uid, [('partner_id', '=', partner.id), ('date_invoice', '>=', form['start_date']), ('date_invoice', '<=', form['end_date']), ('type', '=', 'out_invoice')])
        data_inv = obj_inv.browse(self.cr, self.uid, inv_ids)
        sum_non_member = 0
        sum_member = 0
        self.context['partner_id'] = partner
        for inv in data_inv:
            for line in inv.invoice_line:
                if line.product_id:
                    l_price = pool_obj.get('product.product').price_get(self.cr, self.uid, [line.product_id.id], 'list_price', self.context)[line.product_id.id]
                    m_price = pool_obj.get('product.product').price_get(self.cr, self.uid, [line.product_id.id], 'member_price', self.context)[line.product_id.id]
                    sum_member = sum_member + m_price
                    sum_non_member = sum_non_member + l_price
                else:
                    sum_non_member = sum_non_member + line.price_unit
                    sum_member = sum_member + line.price_unit
        if sum_member > sum_non_member:
            diff = sum_member - sum_non_member
        else:
            diff = sum_non_member - sum_member
        return {'unmember':sum_non_member, 'member':sum_member, 'diff':diff}

report_sxw.report_sxw('report.cci_membership_total_sold', 'res.partner', 'addons/cci_membership/report/report_members_total_sold.rml', parser=total_sold, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

