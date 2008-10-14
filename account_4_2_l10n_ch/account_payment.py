# -*- encoding: utf-8 -*-
from osv import osv, fields

class PaymentMode(osv.osv):
    _inherit = "payment.mode"

    def _auto_init(self, cr):
        super(PaymentMode, self)._auto_init(cr)
        cr.execute('ALTER TABLE payment_mode ALTER COLUMN account DROP NOT NULL')
        cr.commit()

PaymentMode()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

