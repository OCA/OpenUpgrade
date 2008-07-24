# -*- encoding: utf-8 -*-
from osv import fields,osv

class Invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'to_export': fields.boolean('To export'),
        'to_update': fields.boolean('To update'),
        }

    _defaults = {
        'to_export': lambda *a: True,
        'to_update': lambda *a: False,
        }

    def write(self, cr, uid, ids, values, context=None):
        if not values:
            values = {}
        if "to_update" not in values:
            values['to_update'] = True
        return super(Invoice,self).write(cr, uid, ids, values, context)

Invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

