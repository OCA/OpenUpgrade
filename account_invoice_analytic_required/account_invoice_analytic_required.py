# -*- encoding: utf-8 -*-
from osv import fields, osv

class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit="account.invoice.line"
    _description = "Invoice line"
    _columns = {
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account', required=True),
    }

account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

