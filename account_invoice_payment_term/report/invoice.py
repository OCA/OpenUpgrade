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


class AccountInvoice(report_sxw.rml_parse):

    def __init__(self, cursor, user, name, context):
        super(AccountInvoice, self).__init__(cursor, user, name, context)
        self.localcontext.update({
            'time': time,
            'sort_lines': self.sort_lines,
        })

    def sort_lines(self, lines):
        lines = [x for x in lines]
        lines.sort(lambda x, y: cmp(x.date_maturity, y.date_maturity))
        return lines

report_sxw.report_sxw('report.account.invoice.payment.term', 'account.invoice',
        'addons/account_invoice_payment_term/report/invoice.rml',
        parser=AccountInvoice)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

