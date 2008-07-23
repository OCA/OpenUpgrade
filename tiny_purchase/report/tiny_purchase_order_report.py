# -*- encoding: utf-8 -*-

from report import report_sxw
import time

class order(report_sxw.rml_parse):
    def __init(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.tiny_purchase.order', 'tiny_purchase.order', 'addons/tiny_purchase/report/order.rml', parser=order)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

