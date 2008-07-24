# -*- encoding: utf-8 -*-
from osv import fields,osv
import tools
import ir
import pooler


class stock_production_lot(osv.osv):
    _name = 'stock.production.lot'
    _inherit ='stock.production.lot'

    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product'),
        'heatcode_id' : fields.many2one('product.heatcode','HeatCode',ondelete='cascade',required=True,select=True),
        'quality' : fields.char('Quality Information',size=256),
        'localisation' : fields.char('Localisation',size=256),
#        'reservations'
#        'avilable'
    }

stock_production_lot()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

