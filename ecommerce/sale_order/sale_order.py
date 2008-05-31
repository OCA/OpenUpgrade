from osv import fields,osv
import ir
import pooler
import datetime
import time
from tools import config

class ecommerce_sale_order(osv.osv):

    _name='ecommerce.saleorder'
    _columns = {
        'name': fields.char('Order Description',size=64, required=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('done','Done'),
            ('cancel','Cancel')
        ], 'Order State',readonly=True),
        'date_order':fields.date('Date Ordered', required=True),
        'epartner_id':fields.many2one('ecommerce.partner', 'Ecommerce Partner', required=True),
        'epartner_add_id':fields.many2one('ecommerce.partner.address', 'Contact Address'),
        'epartner_shipping_id':fields.many2one('ecommerce.partner.address', 'Shipping Address'),
        'epartner_invoice_id':fields.many2one('ecommerce.partner.address', 'Invoice Address'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True),
        'web_id':fields.many2one('ecommerce.shop', 'Web Shop', required=True),
        'order_lines': fields.one2many('ecommerce.order.line', 'order_id', 'Order Lines'),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
        'epartner_invoice_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], ['invoice'])['invoice'],
        'epartner_add_id': lambda self, cr, uid, context: context.get('partner_id', False) and  self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], ['contact'])['contact'],
        'epartner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], ['delivery'])['deliver']
    }

    def order_draft(self,cr,uid,ids):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def order_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
    
    def order_create_function(self, cr, uid, ids, context={}):
        for order in self.browse(cr, uid, ids, context):
            addid = []  
            if not (order.epartner_id and order.epartner_invoice_id and order.epartner_shipping_id):
                raise osv.except_osv('No addresses !', 'You must assign addresses before creating the order.')
          
            res_prt = self.pool.get('res.partner')
            prt_id = res_prt.search(cr, uid, [('name','=',order.epartner_id.name)])
            res = res_prt.read(cr, uid, prt_id, ['id'], context)
            res_add = self.pool.get('res.partner.address')
            
            if res:
                partner_id = res[0]['id']
                
                prt_add_id =res_add.search(cr,uid,[('partner_id','=',partner_id)])
                res_prt_add = res_add.read(cr,uid,prt_add_id,['id'],context)
                addid = res_prt_add[0]['id']
           
            if not prt_id:     
                partner_id = self.pool.get('res.partner').create(cr, uid, {
                    'name': order.epartner_id.name,
                    'lang':order.epartner_id.lang,
                   })
                order.epartner_id.address
                for addr_type in order.epartner_id.address:
                     addid = self.pool.get('res.partner.address').create(cr, uid, {
                    'name': addr_type.username,
                    'type':addr_type.type,
                    'street':addr_type.street,
                    'street2':addr_type.street2,
                    'partner_id':partner_id,
                    'zip':addr_type.zip,
                    'city':addr_type.city,
                    'state_id':addr_type.state_id.id,
                    'country_id':addr_type.country_id.id,
                    'email':addr_type.email,
                    'phone':addr_type.phone,
                    'fax':addr_type.fax,
                    'mobile':addr_type.mobile,
                })
            data_partner = res_prt.browse(cr,uid,partner_id)
            address_contact = False
            address_invoice = False
            address_delivery = False

            for tmp_addr_var in data_partner.address:
                if tmp_addr_var.type == 'contact':
                    address_contact = tmp_addr_var.id
                  
                if tmp_addr_var.type == 'invoice':
                    address_invoice = tmp_addr_var.id
                   
                if tmp_addr_var.type == 'delivery':
                    address_delivery = tmp_addr_var.id
                 
                if (not address_contact) and (tmp_addr_var.type == 'default'):
                    address_contact = tmp_addr_var.id
                   
                if (not address_invoice) and (tmp_addr_var.type == 'default'):
                    address_invoice = tmp_addr_var.id
                    
                if (not address_delivery) and (tmp_addr_var.type == 'default'):
                     address_delivery = tmp_addr_var.id
           
            if (not address_contact) or (not address_invoice) or (not address_delivery) :
                     raise osv.except_osv('Error','Please Enter Default Address!'); 
               
            pricelist_id=order.pricelist_id.id
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
                order_lines.append((0,0,val))
                      
            order_id = self.pool.get('sale.order').create(cr, uid, {
                'name': order.name,
                'shop_id': order.web_id.id,
                'user_id': uid,
                'note': order.note or '',
                'partner_id': partner_id,
                'partner_invoice_id':address_invoice,  
                'partner_order_id':address_contact,  
                'partner_shipping_id':address_delivery,  
                'pricelist_id': order.pricelist_id.id,
                'order_line':order_lines
            })
            self.write(cr, uid, [order.id], {'state':'done', 'order_id': order_id})
        return True

    def address_set(self, cr, uid, ids, *args):
        
        done = []
        for order in self.browse(cr, uid, ids):
            for a in [order.epartner_shipping_id.id,order.epartner_invoice_id.id]:
                if a not in done:
                    done.append(a)
                    self.pool.get('ecommerce.partner').address_set(cr, uid, [a] )
            self.write(cr, uid, [order.id], {
                'partner_shipping_id': order.epartner_invoice_id.address_id.id,
                'partner_id': order.epartner_invoice_id.address_id.partner_id.id,
                'partner_invoice_id': order.epartner_shipping_id.address_id.id,
           })
        return True
    
    def onchange_epartner_id(self, cr, uid, ids, part):
    
        if not part:
            return {'value':{'epartner_invoice_id': False, 'epartner_shipping_id':False, 'epartner_add_id':False}}
        addr = self.pool.get('ecommerce.partner').address_get(cr, uid, [part], ['delivery','invoice','contact'])
        return {'value':{'epartner_invoice_id': addr['invoice'], 'epartner_add_id':addr['contact'], 'epartner_shipping_id':addr['delivery']}}
    
ecommerce_sale_order()

class ecommerce_order_line(osv.osv):
    _name = 'ecommerce.order.line'
    _description = 'eSale Order line'
    _columns = {
        'name': fields.char('Order Line', size=64, required=True),
        'order_id': fields.many2one('ecommerce.saleorder', 'eOrder Ref'),
        'product_qty': fields.float('Quantity', digits=(16,2), required=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], change_default=True),
        'product_uom_id': fields.many2one('product.uom', 'Unit of Measure',required=True),
        'price_unit': fields.float('Unit Price',digits=(16, int(config['price_accuracy'])), required=True),
    }
   
ecommerce_order_line()




