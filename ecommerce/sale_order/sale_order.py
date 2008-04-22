from osv import fields,osv
import ir
import pooler
import datetime
import time
from tools import config

class sale_order(osv.osv):
    _name='ecommerce.saleorder'
    _description="ecommerce sale order"
    _columns = {
        'name': fields.char('Order Description',size=64, required=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('done','Done'),
            ('cancel','Cancel')
        ],'OrderState', readonly=True),
        'date_order':fields.date('Date Ordered', required=True),
       'epartner_shipping_id':fields.many2one('ecommerce.partner', 'Shipping Address', required=True),
        'epartner_invoice_id':fields.many2one('ecommerce.partner', 'Invoice Address', required=True),
        'partner_id':fields.many2one('res.partner', 'Contact Address'),
        'partner_shipping_id':fields.many2one('res.partner.address', 'Shipping Address'),
        'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address'),      
        'web_id':fields.many2one('shop.basic', 'Web Shop', required=True),
        'web_ref':fields.integer('Web Reference'),
        'order_lines': fields.one2many('ecommerce.order.line', 'order_id', 'Order Lines'),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'ecommerce.saleorder'),                 
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
    }


    def action_draft(self,cr,uid,ids):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def action_done(self,cr,uid,ids):
        for order in self.browse(cr, uid, ids):
            if not (order.partner_id and order.partner_invoice_id and order.partner_shipping_id):
                raise osv.except_osv('No addresses !', 'You must assign addresses before creating the order.')
            
            pricelist_id=order.partner_id.property_product_pricelist.id
            order_lines = []
            for line in order.order_lines:
                val = {
                    'name': line.name,
                    'product_uom_qty': line.product_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.price_unit,
                }
                val_new = self.pool.get('sale.order.line').product_id_change(cr, uid, None, pricelist_id, line.product_id.id, line.product_qty, line.product_uom_id.id, name=line.name)['value']
                del val_new['price_unit']
                del val_new['th_weight']
                val_new['product_uos'] = 'product_uos' in val_new and val_new['product_uos'] and val_new['product_uos'][0] or False
                val.update( val_new )
                val['tax_id'] = 'tax_id' in val and [(6,0,val['tax_id'])] or False
                order_lines.append( (0,0,val))
                order_id = self.pool.get('sale.order').create(cr, uid, {
                'name': order.name,
                'shop_id': order.web_id.id,
                'origin': 'WEB:'+str(order.web_ref),
                'user_id': uid,
                'note': order.note or '',
                'partner_id': order.partner_id.id,
                'partner_invoice_id':order.partner_invoice_id.id,
                'partner_order_id':order.partner_invoice_id.id,
                'partner_shipping_id':order.partner_shipping_id.id,
                'pricelist_id': pricelist_id,
                'order_line': order_lines
            })
            self.write(cr, uid, [order.id], {'state':'done', 'order_id': order_id})
        return True
    
    def action_cancel(self,cr,uid,ids):
            self.write(cr, uid, ids, {'state':'cancel'})
            return True

sale_order()


class ecommerce_order_line(osv.osv):
    _name = 'ecommerce.order.line'
    _description = 'ecomemrce sale order'
    _columns = {
                'name': fields.char('Order Line', size=64, required=True),
                'order_id': fields.many2one('ecommerce.saleorder', 'Eorder Ref.'),
                'product_qty': fields.float('Quantity', digits=(16,2), required=True),
                'product_id': fields.many2one('product.product', 'Product'),
                'product_uom_id': fields.many2one('product.uom', 'Unit of Measure',required=True),
                'price_unit': fields.float('Unit Price',digits=(16,2), required=True),
    }
    
ecommerce_order_line()




