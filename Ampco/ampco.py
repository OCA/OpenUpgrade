from osv import fields,osv
import tools
import ir
import pooler

class product_product(osv.osv):
    _name = "product.template"
    _inherit = "product.template"

    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product'),
        }

product_product()

class sale_order_line(osv.osv):
    _name = "sale.order.line"
    _inherit = "sale.order.line"
    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product')
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False,weight=0, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True):

        datas = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty=0,uom=False,qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True)
        if qty:
            datas['value']['th_weight'] = weight * qty
        else:
            datas['value']['th_weight'] = weight * qty_uos
        return datas
sale_order_line()


class stock_production_lot(osv.osv):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product'),
        'heatcode_id' :  fields.many2one('product.heatcode','Heatcode'),

#Quality information
#Localisation
#Reservations (one2many qty, sizes)
#Availables (computed field)
        }

stock_production_lot()




