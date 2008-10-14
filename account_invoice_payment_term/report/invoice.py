# -*- encoding: utf-8 -*-
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

