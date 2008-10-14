# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from osv import fields,osv

class account_invoice(osv.osv):

    _inherit = "account.invoice"
    _columns = {
        'export_date': fields.datetime("Export time"),
        }

    _defaults = {
        'price_type': lambda *a: 'tax_included',
    }


    def _refund_cleanup_lines(self, lines):
        for line in lines:
            del line['id']
            del line['invoice_id']
            if 'account_id' in line:
                line['account_id'] = line.get('account_id', False) and line['account_id'][0]
            if 'product_id' in line:
                line['product_id'] = line.get('product_id', False) and line['product_id'][0]
            if 'uos_id' in line:
                line['uos_id'] = line.get('uos_id', False) and line['uos_id'][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = [(6,0, line.get('invoice_line_tax_id', [])) ]
            if 'account_analytic_id' in line:
                line['account_analytic_id'] = line.get('account_analytic_id', False) and line['account_analytic_id'][0]
            if 'production_lot_id' in line:
                line['production_lot_id'] = line.get('production_lot_id', False) and line['production_lot_id'][0]
        return map(lambda x: (0,0,x), lines)


account_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

