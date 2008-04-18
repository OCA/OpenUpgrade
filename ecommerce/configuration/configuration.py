import datetime
import time
import netsvc
from osv import fields,osv
import ir
import pooler
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

class smtp_mail_config(osv.osv):
    _description='Mail Server Config'
    _name = "smtp.mail.config"

    _columns = {
        'name':fields.char('Name', size=128, required=True),
        'server_name': fields.char('SMTP Server Name', size=128, required=True),
        'port': fields.integer('SMTP Port', size=64,required=True),
        'from_add': fields.char('Email From',size=255,required=True),
      
    }

    def __init__(self, pool):
        super(smtp_mail_config,self).__init__(pool);
        self.smtpserver = None;
        self.email = None;
    #end def

    def connect(self, cr, uid, id=False):
        server = False
        #smtpserver = None

        if id:
            server = self.read(cr, uid, [id])[0]
        else:
            return False
        #end if

      
        if server:
            self.smtpserver = smtplib.SMTP(str(server['server_name']), server['port']);
            self.smtpserver.set_debuglevel(1)
            self.email = server['from_add']
            return True;
        #end if
        else:

            return False
    #end def
    
   

    def close(self):
        try:
            self.smtpserver.close()
        except Exception,e:
            return False
        #end try

        return True
    #end if

    def sendmail(self, cr, uid, to, subject='', body=''):

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        part1 = MIMEText(body);
        part1.set_type("text/html");
        msg.attach(part1)

        try:
            self.smtpserver.sendmail(self.email, to, msg.as_string())
        except Exception,e:
            return False
        #end if

        return True
    #end def

smtp_mail_config()

class image_display_config(osv.osv):
    _name = 'image.display.config'
    _description = 'Image Size'
    _columns = {
        'name': fields.char('Name',size=128,required=True),
        'height': fields.float('Width',digits=(16,2)),
        'width': fields.float('Height',digits=(16,2)),
        'scale': fields.selection([('px','Pixel'),('in','Inch')],'Scale'),
    }
image_display_config()

class shop_basic(osv.osv):
    _name = "shop.basic"
    _description = "Shop Basic Info"
    _columns = {
        'name': fields.char('Name', size=256),
        'company_id': fields.many2one('res.company', 'Company'),
        'partner_id': fields.many2one('res.company', 'Owner'),
        'country_id': fields.many2one('res.country', 'Country'),
        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'country_id': fields.many2one('res.country', 'Country'),
        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),
        'smtpreply_id': fields.many2one('smtp.mail.config', 'Reply Server'),
        'smtpnews_id': fields.many2one('smtp.mail.config', 'News Server'),
        'tax_decimal_place': fields.integer('Tax Decimal Places'),
        'page_link': fields.integer('Page Links'),
        'simages_id': fields.many2one("image.display.config", 'Small Image'),
        'limages_id': fields.many2one("image.display.config", 'Large Image'),
        'display_search_keyword':fields.boolean('Require  Quick Search'),
        'display_category_cnt': fields.boolean('Require Category Count'),
        'price_with_tax': fields.boolean('Require Price with Tax'),
        'tell_to_friend': fields.boolean('Tell To Friend'),
        'display_cart': fields.boolean('Require  Cart After Shopping'),
        'display_product_name_new': fields.boolean('Require Product Name'),
        'display_manufacturer_name_new': fields.boolean('Require Manufacturer Name'),
        'display_product_image': fields.boolean('Require Product Image'),
        'display_product_price': fields.boolean('Require Product Price'),
        'display_product_quantity': fields.boolean('Require Product Quantity'),
        'display_product_weight': fields.boolean('Require Product Weight'),
        'display_partner_logo':fields.boolean('Require Partner Logo'),
        'display_category_context':fields.boolean('Require Category Context'),
        'display_page_offset':fields.boolean('Require Page Offset'),
        'category':fields.many2many('product.category','etinyshop_category_rel','cat_id','parent_id','Product Categories'),
        'special':fields.one2many('product.special','shop_id','Special Offers'),
        'products':fields.many2many('product.product','etiny_new_product','product','new_product','Products')
     
    }
shop_basic()



class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'category_image': fields.binary('Category Image'),
        'shop_id': fields.many2one("shop.basic", "Web Shop"),
    }
    def write(self, cr, user, ids, values, context={}):
        product_pool = self.pool.get('product.product')
        categ = self.read(cr,user,ids,['shop_id'])[0]
        product_ids = product_pool.search(cr,user,[('categ_id','=',ids[0])])
        if categ['shop_id']:
            product_pool.write(cr,user,product_ids,{'shop_id':categ['shop_id'][0]})
        return super(product_category,self).write(cr, user, ids, values, context)

product_category()


class sale_order(osv.osv):
    _name='eshop.saleorder'
    _columns = {
        'name': fields.char('Order Description',size=64, required=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('done','Done'),
            ('cancel','Cancel')
        ],'OrderState', readonly=True),
        'date_order':fields.date('Date Ordered', required=True),
       'epartner_shipping_id':fields.many2one('res.partner.ecommerce', 'Shipping Address', required=True),
        'epartner_invoice_id':fields.many2one('res.partner.ecommerce', 'Invoice Address', required=True),
        'partner_id':fields.many2one('res.partner', 'Contact Address'),
        'partner_shipping_id':fields.many2one('res.partner.address', 'Shipping Address'),
        'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address'),      
        'web_id':fields.many2one('shop.basic', 'Web Shop', required=True),
        'web_ref':fields.integer('Web Reference'),
        'order_lines': fields.one2many('eshop.order.line', 'order_id', 'Order Lines'),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'eshop.saleorder'),                 
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


class eshop_order_line(osv.osv):
    _name = 'eshop.order.line'
    _description = 'eShop Order line'
    _columns = {
        'name': fields.char('Order Line', size=64, required=True),
        'order_id': fields.many2one('eshop.saleorder', 'Eorder Ref.'),
        'product_qty': fields.float('Quantity', digits=(16,2), required=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], change_default=True),
        'product_uom_id': fields.many2one('product.uom', 'Unit of Measure',required=True),
       'price_unit': fields.float('Unit Price',digits=(16,2), required=True),
    }
    
eshop_order_line()





